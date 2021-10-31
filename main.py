from Modules.reviews_cuter_service import ReviewsCuterService

TOKEN = 'Environment/google_token.json'

service = ReviewsCuterService()
service.download_reviews(TOKEN, '1o8RFQzkMmb9CMlCG-mR2UbsAz82zUes4BXc0pFymguc', 'all')
service.download_black_words(TOKEN, '1cz05A-aY8-FBAE_oDPcqDmR1iyCk_NjzkuDKdYme_yA', 'black-words')
service.tokenize()
dict_ = ['подсветкой', 'шкафа', 'купе', 'прихожую', 'мебели', 'мебель', 'нареканий', 'Качество', 'Работа',
         'уровень', 'ванной', 'изготовления', 'сроки', 'оценка', 'аванс']

service.shortening_review('Мастер изготавливал 3 шкафа - купе с подсветкой в прихожую. Качество превосходное. '
                          'Все сделано в уровень, надежно и без нареканий. Работа заняла всего 2 дня. Так как я '
                          'остался полностью доволен, обратился к этому мастеру также для изготовления мебели для '
                          'ванной. Но жду уже около месяца, аванс оплачен, а мебель до сих пор не готова. Моя оценка '
                          'была бы 5, если бы не сроки.', dict_)

data = service.shortening_reviews('result.json')
