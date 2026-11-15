import urllib.parse
from datetime import datetime, timedelta
import requests
import config

def generate_google_calendar_url(event):
    """
    Gera uma URL direta para inclusão do evento na Google Agenda (Google Calendar)
    sem depender de consentimento de servidor ou tokens adicionais.
    """
    title = event.get('title', 'Compromisso Acadêmico')
    description = event.get('description', '') or ''
    discipline = event.get('discipline', '') or ''
    
    details = f"Disciplina: {discipline}\nTipo: {event.get('event_type', '').upper()}\n\n{description}\n\n[Gerado pelo Sistema de Gerenciamento de Organização Acadêmica]"
    
    event_date = event.get('event_date') # YYYY-MM-DD
    start_time = event.get('start_time') # HH:MM
    end_time = event.get('end_time') # HH:MM
    
    if start_time:
        start_dt = datetime.strptime(f"{event_date} {start_time}", "%Y-%m-%d %H:%M")
        if end_time:
            end_dt = datetime.strptime(f"{event_date} {end_time}", "%Y-%m-%d %H:%M")
            if end_dt <= start_dt:
                end_dt = start_dt + timedelta(hours=1)
        else:
            end_dt = start_dt + timedelta(hours=1)
            
        # Formato ISO compacto UTC/Local: YYYYMMDDTHHMMSS
        dates_param = f"{start_dt.strftime('%Y%m%dT%H%M%S')}/{end_dt.strftime('%Y%m%dT%H%M%S')}"
    else:
        # Evento de dia inteiro
        dt = datetime.strptime(event_date, "%Y-%m-%d")
        next_day = dt + timedelta(days=1)
        dates_param = f"{dt.strftime('%Y%m%d')}/{next_day.strftime('%Y%m%d')}"

    params = {
        'action': 'TEMPLATE',
        'text': title,
        'dates': dates_param,
        'details': details,
        'location': discipline,
        'trp': 'true'
    }
    
    return f"https://calendar.google.com/calendar/render?{urllib.parse.urlencode(params)}"

def verify_google_id_token(id_token):
    """
    Valida um Google ID Token diretamente via endpoint oficial da Google OAuth 2.0.
    """
    if not id_token:
        return None
    try:
        url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Validação básica de audiência se GOOGLE_CLIENT_ID estiver configurado
            if config.GOOGLE_CLIENT_ID and data.get('aud') != config.GOOGLE_CLIENT_ID:
                return None
            return {
                'google_id': data.get('sub'),
                'email': data.get('email'),
                'name': data.get('name') or data.get('email', '').split('@')[0],
                'avatar': data.get('picture')
            }
    except Exception as e:
        print(f"Erro ao verificar token do Google: {e}")
    return None

def generate_ics_calendar(events):
    """Gera conteúdo no padrão iCalendar (.ics) compatível com Google Calendar e outros"""
    ics = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//SIGOA//Sistema de Organizacao Academica//PT-BR",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
    ]
    for ev in events:
        ics.append("BEGIN:VEVENT")
        ics.append(f"UID:event-{ev['id']}@sigoa.local")
        ics.append(f"SUMMARY:{ev['title']}")
        if ev.get('description'):
            desc = ev['description'].replace('\n', '\\n')
            ics.append(f"DESCRIPTION:{desc}")
        if ev.get('discipline'):
            ics.append(f"LOCATION:{ev['discipline']}")
            
        ev_date = ev['event_date'].replace('-', '')
        if ev.get('start_time'):
            t_start = ev['start_time'].replace(':', '') + '00'
            ics.append(f"DTSTART:{ev_date}T{t_start}")
            if ev.get('end_time'):
                t_end = ev['end_time'].replace(':', '') + '00'
                ics.append(f"DTEND:{ev_date}T{t_end}")
            else:
                ics.append(f"DTEND:{ev_date}T{t_start}")
        else:
            ics.append(f"DTSTART;VALUE=DATE:{ev_date}")
            ics.append(f"DTEND;VALUE=DATE:{ev_date}")
            
        ics.append("STATUS:CONFIRMED")
        ics.append("END:VEVENT")
        
    ics.append("END:VCALENDAR")
    return "\r\n".join(ics)
