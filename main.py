from Modules.reviews_cuter_service import ReviewsCuterService

TOKEN = 'Environment/google_token.json'

TABLE = 'mebel'

service = ReviewsCuterService()
service.load_from_tsv_reviews('orders.tsv')
# service.download_reviews(TOKEN, '1o8RFQzkMmb9CMlCG-mR2UbsAz82zUes4BXc0pFymguc', TABLE)
service.download_black_words(TOKEN, '1cz05A-aY8-FBAE_oDPcqDmR1iyCk_NjzkuDKdYme_yA', 'black-words')
service.tokenize()
data = service.shortening_reviews(TABLE+'_report.json')
