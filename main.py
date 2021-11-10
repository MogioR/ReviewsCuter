from Modules.reviews_cuter_service import ReviewsCuterService

TOKEN = 'Environment/google_token.json'

TABLE = 'mebel2'

service = ReviewsCuterService()
service.load_from_tsv_reviews('orders.tsv')
# # service.download_reviews(TOKEN, '1o8RFQzkMmb9CMlCG-mR2UbsAz82zUes4BXc0pFymguc', TABLE)
service.download_black_words(TOKEN, '1cz05A-aY8-FBAE_oDPcqDmR1iyCk_NjzkuDKdYme_yA', 'black-words')
service.tokenize()
review = 'Мастер понравился, цена соответствует качеству. Отлично сделал перетяжку мягкого уголка на кухне. ' \
         'Качественно, красиво, очень оперативно. Спасибо!'
service.shortening_review(review, ['цена', 'перетяжку', 'уголка', 'кухне'])
#data = service.shortening_reviews(TABLE+'_report.json')
