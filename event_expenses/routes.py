from flask import render_template, redirect, url_for, flash, request, send_from_directory
from flask import current_app as app
from event_expenses.extensions import db
from event_expenses.utils import send_styled_email
from event_expenses.models import Event, Participant, Expense
from event_expenses.forms import EventForm, ParticipantForm, ExpenseForm, AccessEventForm, EmailRecoveryForm
from event_expenses.utils import generate_token, confirm_token, send_token_email, generate_event_token, participant_color
from decimal import Decimal, ROUND_HALF_UP

@app.route('/', methods=['GET', 'POST'])
def home():
    access_form = AccessEventForm()
    recover_form = EmailRecoveryForm()

    return render_template('access_event.html', access_form=access_form, recover_form=recover_form)

@app.route('/static/<path:filename>')
def static_file(filename):
    print(f"Serving static file: {filename}")
    return send_from_directory(app.static_folder, filename)

@app.route('/access', methods=['POST'])
def access_event():
    access_form = AccessEventForm()

    # Accedir a l'event existent
    if access_form.submit.data and access_form.validate_on_submit():
        token = access_form.token.data
        event = Event.query.filter_by(token=token, validated=True, archived=False).first_or_404()
        if event:
            flash('Accedint al teu event.', 'success')
            return redirect(url_for('event_summary', event_token=event.token))
        else:
            flash('Token invàlid o event no validat.', 'danger')

    return redirect(url_for('home'))


@app.route('/recover', methods=['POST'])
def recover_events():
    recover_form = EmailRecoveryForm()
    if recover_form.validate_on_submit():
        email = recover_form.email.data
        events = Event.query.filter_by(email=email, validated=True, archived=False).all()
        
        if not events:
            flash('T\'hem enviat un correu amb els teus events registrats.', 'success')  
            return redirect(url_for('home'))

        # Enviar correu amb la llista d'events
        body_html = f"""
        <h2>Els teus events actius a Splitly</h2>
        <p>Pots accedir-hi amb els següents enllaços:</p>
        <ul>
        """
        for event in events:
            body_html += f"""
            <li>
                <strong>{event.name}</strong> - 
                <a href="{url_for('event_summary', event_token=event.token, _external=True)}">
                    Accedir a l'event
                </a>
            </li>
            """
        body_html += """
        </ul>
        <p>Si no reconeixes aquests events, contacta amb nosaltres.</p>
        <p>Gràcies per utilitzar Splitly!</p>
        """

       
        send_styled_email(
            subject="🎉 El teu event Splitly està llest!",
            recipients=[email],
            body_html=body_html
        )
        flash('T\'hem enviat un correu amb els teus events registrats.', 'success')
        return redirect(url_for('home'))

    return redirect(url_for('home'))

@app.route('/create_event', methods=['GET', 'POST'])
def create_new_event():
    event_form = EventForm()
    # Crear nou event
    print("Creating new event with form data:", event_form.data)
    if event_form.submit.data and event_form.validate_on_submit():
        print("Creating new event with form data:", event_form.data)
        validation_token = generate_token(event_form.email.data)
        event = Event(
            name=event_form.name.data,
            description=event_form.description.data,
            email=event_form.email.data,
            validation_token=validation_token
        )
        db.session.add(event)
        db.session.commit()

        # Enviar correu de validació
        validation_link = url_for('validate_event', validation_token=validation_token, _external=True)
        body_html = f"""
        <h2>El teu event {event.name} s'ha creat!</h2>
        <p>Fes clic aquí per validar el teu event: {validation_link}</p>
        """
        send_styled_email(
            subject="🎉 Ja pots validar el teu event Splitly!",
            recipients=[event_form.email.data],
            body_html=body_html
        )

        flash('Event creat! Revisa el teu correu per validar-lo.', 'success')
        return redirect(url_for('home'))
    # Si el formulari no s'ha enviat o hi ha errors, renderitzem el formulari
    if event_form.errors:
        for field, errors in event_form.errors.items():
            for error in errors:
                flash(f'Error en {field}: {error}', 'danger')   
    
    return render_template('create_event.html', event_form=event_form)

    
@app.route('/validate/<validation_token>')
def validate_event(validation_token):
    email = confirm_token(validation_token)
    if not email:
        flash('Enllaç de validació invàlid o caducat.', 'danger')
        return redirect(url_for('create_event'))

    event = Event.query.filter_by(validation_token=validation_token, archived=False).first_or_404()
    if event:
        event.validated = True
        event.token = generate_event_token(length=8)
        event.validation_token = None  # Clear validation token after validation
        db.session.commit()

        body_html = f"""
            <h2>El teu event {event.name} ja està actiu!</h2>
            <p>Pots accedir-hi amb el següent enllaç:</p>
            <a href="{url_for('event_summary', event_token=event.token, _external=True)}" class="button">
                Obrir el meu viatge
            </a>
            """

        send_styled_email(
            subject="🎉 El teu event Splitly està llest!",
            recipients=[email],
            body_html=body_html
        )

        flash('Event validat correctament!', 'success')
    else:
        flash('No s\'ha trobat l\'event corresponent.', 'warning')
    return render_template('validate_event.html', event=event)

@app.route('/event/<event_token>/archive', methods=['POST'])
def archive_event(event_token):
    event = Event.query.filter_by(token=event_token).first_or_404()
    event.archived = True
    db.session.commit()
    flash('L\'event ha estat arxivat.', 'info')
    return redirect(url_for('home'))

@app.route('/event/<event_token>/participants', methods=['GET', 'POST'])
def manage_group(event_token):
    event = Event.query.filter_by(token=event_token, archived=False).first_or_404()
    if not event:
        flash('Event no trobat.', 'danger')
        return redirect(url_for('access_event'))
    if not event.validated:
        flash('Aquest event encara no ha estat validat.', 'warning')
        return redirect(url_for('create_event'))

    form = ParticipantForm()
    form.event_id.data = event.id

    if form.validate_on_submit():
        participant = Participant(
            name=form.name.data,
            num_people=form.num_people.data,
            email=form.email.data,
            event_id=event.id
        )
        db.session.add(participant)
        db.session.commit()
        if form.send_email.data and participant.email:
            send_token_email(participant.email, event.token, event.name)
            flash('Participant afegit i correu enviat.', 'success')
        else:
            flash('Participant afegit sense enviar correu.', 'success')
        return redirect(url_for('manage_group', event_token=event.token))
    
    participants = Participant.query.filter_by(event_id=event.id).all()     
    participant_colors = {
        p.id: participant_color(p.name or str(p.id))
        for p in participants
    }

    return render_template('manage_group.html', event=event, participants=participants, 
                           form=form, participant_colors=participant_colors)

@app.route('/event/<event_token>/expenses', methods=['GET', 'POST'])
def add_expense(event_token):
    event = Event.query.filter_by(token=event_token, archived=False).first_or_404()
    if not event:
        flash('Viatge no trobat.', 'danger')
        return redirect(url_for('access_event'))
    if not event.validated:
        flash('Aquest event encara no ha estat validat.', 'warning')
        return redirect(url_for('create_event'))

    form = ExpenseForm()
    participants = Participant.query.filter_by(event_id=event.id).all()

    form.payer_id.choices = [(p.id, p.name) for p in participants]
    form.split_between.choices = [(p.id, p.name) for p in participants]

    if form.validate_on_submit():
        expense = Expense(
            description=form.description.data,
            amount=form.amount.data,
            payer_id=form.payer_id.data,
            split_between=','.join(str(pid) for pid in form.split_between.data),
            event_id=event.id
        )
        db.session.add(expense)
        db.session.commit()
        flash('Despesa afegida correctament.', 'success')
        return redirect(url_for('add_expense', event_token=event.token))
    
    participant_colors = {
        p.id: participant_color(p.name or str(p.id))
        for p in participants
    }

    expenses = Expense.query.filter_by(event_id=event.id).order_by(Expense.date.desc()).all()
    total_amount = sum(exp.amount for exp in expenses)

    return render_template('add_expense.html', event=event, form=form, expenses=expenses, 
                           participants={p.id: p.name for p in participants},
                           participant_colors=participant_colors, total_amount=total_amount)

@app.route('/event/<event_token>/summary')
def event_summary(event_token):
    event = Event.query.filter_by(token=event_token, archived=False).first_or_404()
    if not event:
        flash('Viatge no trobat.', 'danger')
        return redirect(url_for('access_event'))
    if not event.validated:
        flash('Aquest event encara no ha estat validat.', 'warning')
        return redirect(url_for('create_event'))
    
    participants = Participant.query.filter_by(event_id=event.id).all()
    expenses = Expense.query.filter_by(event_id=event.id).all()

    participant_names = {p.id: p.name for p in participants}
    participant_weights = {p.id: p.num_people for p in participants}

    paid = {p.id: Decimal('0.0') for p in participants}
    owed = {p.id: Decimal('0.0') for p in participants}

    for e in expenses:
        paid[e.payer_id] += Decimal(str(e.amount))

        split_ids = [int(pid) for pid in e.split_between.split(',') if pid]

        if split_ids:
            total_weight = sum(participant_weights[pid] for pid in split_ids)

            for pid in split_ids:
                weight = participant_weights[pid]
                share = Decimal(str(e.amount)) * Decimal(weight) / Decimal(total_weight)
                owed[pid] += share

    # Càlcul del balanç
    balances = {}
    for pid in paid:
        balance = paid[pid] - owed[pid]
        if abs(balance) < Decimal('0.01'):
            balance = Decimal('0.0')
        balances[pid] = balance

    # Generem transferències recomanades
    debtors = [(pid, amt) for pid, amt in balances.items() if amt < 0]
    creditors = [(pid, amt) for pid, amt in balances.items() if amt > 0]

    debtors.sort(key=lambda x: x[1])  # més negatiu primer
    creditors.sort(key=lambda x: x[1], reverse=True)  # més positiu primer

    transfers = []

    for d_id, d_amt in debtors:
        d_amt = -d_amt  # passem a positiu

        for i in range(len(creditors)):
            c_id, c_amt = creditors[i]
            if c_amt <= 0:
                continue

            amount = min(d_amt, c_amt)
            amount = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            if amount > 0:
                transfers.append({
                    'from': participant_names[d_id],
                    'to': participant_names[c_id],
                    'amount': float(amount)
                })

                balances[d_id] -= amount
                balances[c_id] -= amount
                d_amt -= amount

                creditors[i] = (c_id, balances[c_id])  # actualitza saldo

            if d_amt <= 0:
                break

    # Prepara dades per a la gràfica
    chart_data = [
        {
            'name': participant_names[pid],
            'balance': float((paid[pid] - owed[pid]).quantize(Decimal('0.01')))
        }
        for pid in paid
    ]

    return render_template(
        'summary.html',
        event=event,
        names=participant_names,
        transfers=transfers,
        chart_data=chart_data
    )



@app.route('/expense/<int:expense_id>/edit', methods=['GET', 'POST'])
def edit_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    event = Event.query.get_or_404(expense.event_id)
    form = ExpenseForm()

    participants = Participant.query.filter_by(event_id=event.id).all()
    form.payer_id.choices = [(p.id, p.name) for p in participants]
    form.split_between.choices = [(p.id, p.name) for p in participants]

    if request.method == 'GET':
        form.description.data = expense.description
        form.amount.data = expense.amount
        form.payer_id.data = expense.payer_id
        form.split_between.data = [int(pid) for pid in expense.split_between.split(',')]

    if form.validate_on_submit():
        expense.description = form.description.data
        expense.amount = form.amount.data
        expense.payer_id = form.payer_id.data
        expense.split_between = ','.join(str(pid) for pid in form.split_between.data)
        db.session.commit()
        flash('Despesa actualitzada.', 'success')
        return redirect(url_for('add_expense', event_token=event.token))

    return render_template('edit_expense.html', event=event, form=form, expense=expense)


@app.route('/expense/<int:expense_id>/delete', methods=['POST'])
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    event_id = expense.event_id
    db.session.delete(expense)
    db.session.commit()
    flash('Despesa eliminada.', 'success')
    return redirect(url_for('add_expense', event_id=event_id))

@app.route('/event/<token>/participants/<int:participant_id>/delete', methods=['POST'])
def delete_participant(token, participant_id):
    event = Event.query.filter_by(token=token).first_or_404()
    participant = Participant.query.get_or_404(participant_id)

    # Validació
    has_paid = Expense.query.filter_by(payer_id=participant.id, event_id=event.id).count() > 0
    event_expenses = Expense.query.filter(Expense.event_id == event.id)
    for expense in event_expenses:
        is_involved = participant.id in [int(pid) for pid in expense.split_between.split(',') if pid]
        if is_involved:
            break

    if has_paid or is_involved:
        flash("Aquest participant no es pot eliminar perquè té despeses o deutes associats.", "danger")
        return redirect(url_for('manage_group', event_token=event.token))

    db.session.delete(participant)
    db.session.commit()
    flash("Participant eliminat correctament.", "success")
    return redirect(url_for('manage_group', event_token=event.token))


## Modal routes
@app.route('/event/<event_token>/expense_form_modal', methods=['GET'])
def expense_form_modal(event_token):
    expense_id = request.args.get('expense_id', type=int)
    event = Event.query.filter_by(token=event_token, archived=False).first_or_404()
    if not event:
        flash('Viatge no trobat.', 'danger')
        return redirect(url_for('access_event'))
    if not event.validated:
        flash('Aquest event encara no ha estat validat.', 'warning')
        return redirect(url_for('create_event'))
    participants = Participant.query.filter_by(event_id=event.id).all()

    form = ExpenseForm()
    form.payer_id.choices = [(p.id, p.name) for p in participants]
    form.split_between.choices = [(p.id, p.name) for p in participants]

    if expense_id:
        expense = Expense.query.get_or_404(expense_id)
        form.description.data = expense.description
        form.amount.data = expense.amount
        form.payer_id.data = expense.payer_id
        form.split_between.data = [int(pid) for pid in expense.split_between.split(',')]
        return render_template('partials/expense_form.html', form=form, event=event, edit=True, expense_id=expense.id)
    else:
        return render_template('partials/expense_form.html', form=form, event=event, edit=False)


### funcions que no es fan servir 

# @app.route('/expense/<int:expense_id>/edit_modal')
# def edit_expense_modal(expense_id):
#     expense = Expense.query.get_or_404(expense_id)
#     event = Event.query.get_or_404(expense.event_id)
#     form = ExpenseForm()

#     participants = Participant.query.filter_by(event_id=event.id).all()
#     form.payer_id.choices = [(p.id, p.name) for p in participants]
#     form.split_between.choices = [(p.id, p.name) for p in participants]

#     form.description.data = expense.description
#     form.amount.data = expense.amount
#     form.payer_id.data = expense.payer_id
#     form.split_between.data = [int(pid) for pid in expense.split_between.split(',')]

#     return render_template('partials/expense_form.html', form=form, event=event, expense=expense)

# @app.route('/event/<int:event_id>/add_participant_modal')
# def add_participant_modal(event_id):
#     event = Event.query.get_or_404(event_id)
#     form = ParticipantForm()
#     form.event_id.data = event.id
#     return render_template('partials/participant_form.html', form=form, event=event)
