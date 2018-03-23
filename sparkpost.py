from sparkpost import SparkPost
import config

emails = SparkPost(config.SPARKPOST_KEY)
