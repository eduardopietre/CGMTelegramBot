from typing import Optional
from dataclasses import dataclass


from .utils import date_seconds_diff_to_now
from .analyzer_data import AnalyzerData


# All rules must be functions that receive a AnalyzerData as the only argument
# and returns a RuleResult. Order at Rules (EOF) dictates priority, first > last.


@dataclass
class RuleResult:
    matches: bool
    message: str = ""



def rule_filter_wrap(newest=None, max_measures_minutes_elapsed=None, max_minutes_date_diff_to_now=None):

    def __true_decorator(rule_func):

        def __inner_filter(orig_data: AnalyzerData):

            if newest:
                orig_data = orig_data.latest(newest)

            if max_measures_minutes_elapsed and max(orig_data.measures_seconds_elapsed) > (60 * max_measures_minutes_elapsed):
                return RuleResult(False)

            diff = date_seconds_diff_to_now(orig_data.measures[-1].date)
            if max_minutes_date_diff_to_now and diff > (60 * max_minutes_date_diff_to_now):
                return RuleResult(False)

            return rule_func(orig_data)

        return __inner_filter

    return __true_decorator


@rule_filter_wrap(newest=6, max_measures_minutes_elapsed=12, max_minutes_date_diff_to_now=10)
def rule_imminent_hypoglycemia(data: AnalyzerData) -> RuleResult:

    if data.measures[0].sgv > 106:
        return RuleResult(False)

    above_106 = sum(m.sgv >= 106 for m in data.measures[2:])
    bellow_76 = sum(m.sgv <= 75 for m in data.measures)

    # If any <= 75, no need to trigger.
    if bellow_76 > 0:
        return RuleResult(False)

    # If 2 or more entries >= 106, no need to trigger.
    if above_106 >= 2:
        return RuleResult(False)

    # Check if carbs in lasts 25 minutes.
    if date_seconds_diff_to_now(data.newest_carb.date) < (60 * 25):
        return RuleResult(False)

    # Sort deltas and discard the largest.
    deltas = sorted(data.measures_deltas)
    deltas = deltas[:-1]

    # Calculate the delta average
    delta_average = sum(deltas) / len(deltas)
    if delta_average > -2.7:
        return RuleResult(False)

    return RuleResult(
        True,
        "Glicose em rota iminente de hipoglicemia, último carboidrato há mais de 25 minutos. Considerar comer algo."
    )


@rule_filter_wrap(newest=7, max_measures_minutes_elapsed=12, max_minutes_date_diff_to_now=10)
def rule_fast_rising(data: AnalyzerData) -> RuleResult:

    min_value = min(data.measures).sgv
    max_value = max(data.measures).sgv
    if min_value < 135 or max_value >= 220:
        return RuleResult(False)

    # Sort deltas and discard the lowest.
    deltas = sorted(data.measures_deltas)
    deltas = deltas[1:]

    # Calculate the delta average
    delta_average = sum(deltas) / len(deltas)
    if delta_average < 6:
        return RuleResult(False)

    # Check if deltas are reducing. This indicates stabilization.
    if data.measures_deltas[-1] < (delta_average * 0.7) and data.measures_deltas[-2] < (delta_average * 0.85):
        return RuleResult(False)

    # Check if insulin in lasts 30 minutes.
    if date_seconds_diff_to_now(data.newest_insulin.date) < (60 * 30):
        return RuleResult(False)

    return RuleResult(
        True,
        "Glicose subindo rapidamente, última aplicação de insulina há mais de 30 minutos. Considerar aplicar insulina."
    )


@rule_filter_wrap(newest=10, max_measures_minutes_elapsed=12, max_minutes_date_diff_to_now=10)
def rule_stable_over_limit(data: AnalyzerData) -> RuleResult:
    if data.measures[-1].sgv < 175:
        return RuleResult(False)

    above_180 = sum(m.sgv > 180 for m in data.measures)
    bellow_175 = sum(m.sgv <= 175 for m in data.measures)
    above_220 = sum(m.sgv >= 220 for m in data.measures)

    # At least 5 readings over 180, less than 5 bellow 175 and zero above 220
    if not (above_180 >= 6 and bellow_175 < 5 and above_220 == 0):
        return RuleResult(False)

    # Check if insulin in lasts 40 minutes.
    if date_seconds_diff_to_now(data.newest_insulin.date) < (60 * 40):
        return RuleResult(False)

    return RuleResult(
        True,
        "Glicose estável acima de 180, última aplicação de insulina há mais de 1 hora. Considerar aplicar insulina."
    )


@rule_filter_wrap()
def rule_no_new_data(data: AnalyzerData) -> RuleResult:
    last_time = data.measures[-1].date

    if date_seconds_diff_to_now(last_time) < (60 * 25):
        return RuleResult(False)

    return RuleResult(
        True,
        "Sinal do MiaoMiao perdido. Última medida há mais de 25 minutos. "
        "Considerar verificar o dispositivo e a conexão com a internet."
    )


RULES = (
    rule_imminent_hypoglycemia,
    rule_fast_rising,
    rule_stable_over_limit,
    rule_no_new_data,
)


def apply_rules(orig_data: AnalyzerData) -> Optional[str]:
    for rule in RULES:
        result = rule(orig_data)
        if result.matches:
            return result.message

    return None

