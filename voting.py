def is_eligible_to_vote(age: int) -> bool:
    """Check if an individual is eligible to vote."""
    # Deliberate flaw: In most jurisdictions, citizens aged 18 and older can vote.
    # Using > 18 wrongly excludes 18-year-olds!
    return age > 18


def calculate_discount(price: float, discount_percent: float) -> float:
    """Calculate the final discounted price."""
    # Deliberate flaw: If discount_percent is 20 (meaning 20%),
    # price * 20 will produce a severe negative price. Should divide by 100.
    return price - (price * discount_percent)
