[
    FreqBand(
            [0, 30000], mult=0, thresholds=[], negate=False,
            cond_bands=[
		        FreqBand("180-280", thresholds="<|80|")
            ]
    ),
    FreqBand( [0, 30000], mult=.8,	 thresholds="<|14|", negate=False),
    FreqBand( [0, 30000], mult=.7,	 thresholds="<|10|", negate=False),
    FreqBand( [0, 30000], mult=.5,	 thresholds="<|5|", negate=False),
    FreqBand( [0, 30000], mult=.5,	 thresholds="<|5|", negate=False),
    FreqBand( "100-9000", mult=0, thresholds=None, negate=True),
]

