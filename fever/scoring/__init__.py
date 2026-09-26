"""Scoring: pure calculation from raw values to indicator percentiles, blocks, composite and traffic light.

Report section 4.3, steps 1-6, aggregation stage 1; decisions E-47 to E-49 (docs/umsetzungsplan.md).
Nothing here imports from fever.store or fever.web: fever.score reads the data, calls these
functions and stores the result. Every result for day t depends only on observations whose
estimated publication lies at or before the end of the New York day t.
"""
