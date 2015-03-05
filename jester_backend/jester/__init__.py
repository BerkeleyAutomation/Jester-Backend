from models import UserLog
from models import RecommenderLog

log_rating = UserLog.log_rating
log_request_joke = UserLog.log_request_joke
log_logout = UserLog.log_logout

log_prediction = RecommenderLog.log_prediction
log_averages = RecommenderLog.log_averages
log_cluster_choice = RecommenderLog.log_cluster_choice