# def viewed_pages(get_response):
#     def middleware(request):
#         path = request.path
#         if not path.startswith(
#             (
#                 '/media',
#                 '/static',
#                 '/fonts',
#                 '/forms',
#                 '/cart/add_ready_product_list',
#                 '/cart/change',
#                 '/cart/change_comment',
#                 '/cart/delete_product',
#                 '/cart/clear',
#                 '/cart/total_count',
#                 '/cart/send_cart',
#                 '/cart/setup_layout',
#                 '/cart/submit_order',
#             )
#         ):
#             pages = request.session.get('viewed_pages', [])
#             if path not in pages:
#                 pages.append(path)
#             if len(pages) > 5:
#                 pages = pages[1:]
#             request.session['viewed_pages'] = pages
#         # response = get_response(request)
#         return response
#
#     return middleware
