

PHQ9_QUESTIONS = [
    "Little interest or pleasure in doing things?",
    "Feeling down, depressed, or hopeless?",
    "Trouble falling or staying asleep, or sleeping too much?",
    "Feeling tired or having little energy?",
    "Poor appetite or overeating?",
    "Feeling bad about yourself — or that you are a failure or have let yourself or your family down?",
    "Trouble concentrating on things, such as reading the newspaper or watching television?",
    "Moving or speaking so slowly that other people could have noticed? Or the opposite — being so fidgety or restless that you have been moving a lot more than usual?",
    "Thoughts that you would be better off dead or of hurting yourself in some way?"
]

GAD7_QUESTIONS = [
    "Feeling nervous, anxious, or on edge?",
    "Not being able to stop or control worrying?",
    "Worrying too much about different things?",
    "Trouble relaxing?",
    "Being so restless that it is hard to sit still?",
    "Becoming easily annoyed or irritable?",
    "Feeling afraid as if something awful might happen?"
]

RESPONSE_OPTIONS = [
    ("Not at all", 0),
    ("Several days", 1),
    ("More than half the days", 2),
    ("Nearly every day", 3)
]

def calculate_phq9_score(responses):
    total = sum(responses)
    if total < 5:
        severity = "Minimal"
    elif total < 10:
        severity = "Mild"
    elif total < 15:
        severity = "Moderate"
    elif total < 20:
        severity = "Moderately severe"
    else:
        severity = "Severe"
    return total, severity

def calculate_gad7_score(responses):
    total = sum(responses)
    if total < 5:
        severity = "Minimal"
    elif total < 10:
        severity = "Mild"
    elif total < 15:
        severity = "Moderate"
    else:
        severity = "Severe"
    return total, severity
