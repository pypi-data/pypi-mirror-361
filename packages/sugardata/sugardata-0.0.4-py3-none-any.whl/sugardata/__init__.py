import warnings
warnings.filterwarnings("ignore", message=".*Series.__getitem__ treating keys as positions is deprecated.*")

from .tasks.sentiment.service import (
    augment_sentiment_data, augment_sentiment_data_async, augment_sentiment_multi_vendor_async,
    generate_sentiment_data, generate_sentiment_data_async, generate_sentiment_multi_vendor_async
)

__all__ = [
    "augment_sentiment_data",
    "augment_sentiment_data_async",
    "augment_sentiment_multi_vendor_async",
    "generate_sentiment_data",
    "generate_sentiment_data_async",
    "generate_sentiment_multi_vendor_async"
]

__version__ = '0.0.4'