import re
import unicodedata
from datetime import date, timedelta
from pypdf import PdfReader

MONTHS = {
    'JANEIRO': 1, 'FEVEREIRO': 2, 'MARCO': 3, 'ABRIL': 4,
    'MAIO': 5, 'JUNHO': 6, 'JULHO': 7, 'AGOSTO': 8,
    'SETEMBRO': 9, 'OUTUBRO': 10, 'NOVEMBRO': 11, 'DEZEMBRO': 12,
}
WEEKDAYS = ('segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado')
TIME_RE = re.compile(r'\b(\d{1,2}:\d{2})\b')
ROOM_RE = re.compile(r'\((?:sala\s*\d+|lab(?:oratorio)?\s*\d+)\)', re.I)


def _plain(value):
    value = unicodedata.normalize('NFD', value or '')
    value = ''.join(ch for ch in value if unicodedata.category(ch) != 'Mn').upper()
    value = value.replace('\ufffd', '')
    return value.replace('INCIO', 'INICIO').replace('PERODO', 'PERIODO').replace('TERA', 'TERCA').replace('SBADO', 'SABADO')


def read_academic_calendar(stream, semester=None):
    reader = PdfReader(stream)
    pages = [(page.extract_text() or '') for page in reader.pages]
    text = _plain('\n'.join(pages))
    if not text.strip():
        raise ValueError('O calendario academico nao contem texto selecionavel.')

    period_starts = list(re.finditer(r'(\d{2}/\d{2}/\d{4})\s+INICIO DO PERIODO LETIVO\s+(\d{4}/\d)', text))
    if semester is None:
        if not period_starts:
            raise ValueError('Nao encontrei datas de inicio dos periodos letivos no calendario.')
        semester = period_starts[-1].group(2)
    start_match = next((m for m in period_starts if m.group(2) == semester), None)
    if not start_match:
        raise ValueError(f'O calendario nao contem o periodo letivo {semester}.')
    end_match = re.search(r'(\d{2}/\d{2}/\d{4})\s+ENCERRAMENTO DO PERIODO LETIVO\s+' + re.escape(semester), text)
    if not end_match:
        raise ValueError(f'Nao encontrei a data de encerramento do periodo {semester}.')
    start = date.fromisoformat('-'.join(reversed(start_match.group(1).split('/'))))
    end = date.fromisoformat('-'.join(reversed(end_match.group(1).split('/'))))
    if end < start or (end - start).days > 250:
        raise ValueError('O periodo letivo encontrado no calendario parece invalido.')

    teaching_dates = set()
    month_header = re.compile(r'\b(' + '|'.join(MONTHS) + r')\s+(\d{4})\s+DIAS LETIVOS\s*:?\s*\d+', re.I)
    for page_text in pages:
        normalized = _plain(page_text)
        matches = list(month_header.finditer(normalized))
        for index, match in enumerate(matches):
            block_end = normalized.find(match.group(1) + ' DE ' + match.group(2), match.end())
            if block_end < 0:
                block_end = matches[index + 1].start() if index + 1 < len(matches) else len(normalized)
            block = normalized[match.end():block_end]
            month, year = MONTHS[match.group(1)], int(match.group(2))
            for day_match in re.finditer(r'(?<!\d)(\d{1,2})\s*(L|NL|FE|AP|RP|SPI(?:-C)?|F)(?![A-Z])', block):
                day_num = int(day_match.group(1))
                if day_match.group(2) == 'L':
                    try:
                        d = date(year, month, day_num)
                    except ValueError:
                        continue
                    if start <= d <= end:
                        teaching_dates.add(d.isoformat())
    if not teaching_dates:
        raise ValueError('Encontrei o periodo letivo, mas nao consegui ler os dias letivos da tabela do calendario.')
    return (start, end), teaching_dates


def _spans(page):
    output = []
    def visitor(text, cm, tm, font, size):
        value = (text or '').strip()
        if value:
            output.append({'text': value, 'x': float(tm[4]), 'y': float(tm[5])})
    page.extract_text(visitor_text=visitor)
    return output


def read_course_semester(stream):
    reader = PdfReader(stream)
    text = _plain('\n'.join(page.extract_text() or '' for page in reader.pages))
    match = re.search(r'SEMESTRE\D{0,24}(\d{4}/\d)', text)
    if not match:
        raise ValueError('Nao encontrei o semestre no PDF do horario do curso.')
    return match.group(1)


def read_course_schedule(stream, phase):
    reader = PdfReader(stream)
    records = []
    full_text = _plain('\n'.join(page.extract_text() or '' for page in reader.pages))
    for page_number, page in enumerate(reader.pages, 1):
        spans = _spans(page)
        page_text = page.extract_text() or ''
        phase_positions = []
        # PDF visitor splits e.g. "6a fase" across three text fragments.
        for span in spans:
            if _plain(span['text']).strip() == 'FASE':
                nearby = [s for s in spans if abs(s['y'] - span['y']) < 1.5 and 0 <= span['x'] - s['x'] < 32 and re.search(r'\d', s['text'])]
                if nearby:
                    number = int(re.search(r'\d+', nearby[-1]['text']).group())
                    phase_positions.append((number, span['y']))
        if not phase_positions:
            continue

        # Collect day column centers from the weekday heading immediately above each phase grid.
        headings = []
        for span in spans:
            value = _plain(span['text']).lower()
            for day_index, word in enumerate(WEEKDAYS):
                if value.startswith(word):
                    headings.append((day_index, span['x'], span['y']))
                    break

        rows = []
        by_y = {}
        for span in spans:
            if span['x'] < 115 and TIME_RE.search(span['text']):
                by_y.setdefault(round(span['y'], 1), []).append(span)
        for y, row_spans in by_y.items():
            times = TIME_RE.findall(' '.join(s['text'] for s in row_spans))
            if len(times) >= 2:
                rows.append((y, times[0], times[1]))
        rows.sort(reverse=True)

        for row_index, (y, start_time, end_time) in enumerate(rows):
            current_phase = [p for p in phase_positions if p[1] > y]
            if not current_phase:
                continue
            phase_top = min(current_phase, key=lambda p: p[1])
            active_phase = phase_top[0]
            if active_phase != phase:
                continue
            next_phase_y = max((p[1] for p in phase_positions if p[1] < phase_top[1]), default=-1)
            following = [r[0] for r in rows[row_index + 1:] if r[0] > next_phase_y]
            lower_y = max(following) if following else y - 60
            header_candidates = [h for h in headings if phase_top[1] > h[2] > max(next_phase_y, y)]
            if not header_candidates:
                continue
            header_y = max(h[2] for h in header_candidates)
            centers = [(d, x) for d, x, hy in header_candidates if abs(hy - header_y) < 3.0]

            line_spans = [s for s in spans if lower_y < s['y'] <= y + 2.0 and s['x'] > 110]
            room_spans = [s for s in line_spans if ROOM_RE.search(s['text'])]
            for room_span in room_spans:
                if not centers:
                    continue
                day_index, center = min(centers, key=lambda item: abs(item[1] - room_span['x']))
                nearby = [s for s in line_spans if lower_y < s['y'] <= y + 2.0
                          and abs(s['x'] - room_span['x']) < 58
                          and 0 <= s['y'] - room_span['y'] <= 24
                          and not ROOM_RE.search(s['text'])]
                # The acronym is the closest uppercase token above the room label.
                code_candidates = []
                for candidate in nearby:
                    token = _plain(candidate['text']).strip()
                    if re.fullmatch(r'[A-Z][A-Z0-9]{0,8}', token):
                        code_candidates.append(candidate)
                if not code_candidates:
                    continue
                code_span = min(code_candidates, key=lambda s: (abs(s['x'] - room_span['x']), s['y'] - room_span['y']))
                code = _plain(code_span['text']).strip()
                # Preserve section labels such as T1/T2 when they wrap to the right of the acronym.
                suffixes = [s for s in line_spans if abs(s['y'] - code_span['y']) < 1.5
                            and code_span['x'] < s['x'] < code_span['x'] + 65
                            and re.fullmatch(r'T[12]', _plain(s['text']).strip())]
                if suffixes:
                    code += ' ' + _plain(min(suffixes, key=lambda s: s['x'])['text']).strip()
                room = ROOM_RE.search(room_span['text']).group(0).strip('()')
                records.append({'weekday': day_index, 'code': code, 'discipline': code,
                                'room': room, 'start': start_time, 'end': end_time})

    # Read the course names from the subject list printed below each phase grid.
    subject_names = {}
    for record in records:
        code = record['code']
        if code in subject_names:
            continue
        code_pattern = re.escape(code).replace(r'\ ', r'\s+')
        match = re.search(r'\b' + code_pattern + r'\s+FACET-[A-Z]+-\d+\s*-?\s*(.*?)\s+\d{2,3}\s+', full_text, re.S)
        if match:
            subject_names[code] = re.sub(r'\s+', ' ', match.group(1)).strip(' -')
        elif code == 'TCC':
            match = re.search(r'\bTCC\s+II\s+FACET-[A-Z]+-\d+\s*-?\s*(.*?)\s+\d{2,3}\s+', full_text, re.S)
            if match:
                subject_names[code] = re.sub(r'\s+', ' ', match.group(1)).strip(' -')

    # Merge adjacent 55-minute cells for the same lesson and deduplicate repeated PDF text fragments.
    unique = {(r['weekday'], r['code'], r['room'], r['start'], r['end']): r for r in records}
    ordered = sorted(unique.values(), key=lambda r: (r['weekday'], r['code'], r['room'], r['start']))
    merged = []
    for record in ordered:
        previous = next((item for item in reversed(merged) if item['weekday'] == record['weekday']
                         and item['code'] == record['code'] and item['room'] == record['room']), None)
        if previous and previous['end'] == record['start']:
            previous['end'] = record['end']
        else:
            merged.append(dict(record))
    if not merged:
        raise ValueError(f'Nao consegui interpretar a grade da {phase}a fase. Use o PDF de horario do curso em formato pesquisavel.')
    for record in merged:
        record['discipline'] = subject_names.get(record['code'], record['code'])
    return merged
