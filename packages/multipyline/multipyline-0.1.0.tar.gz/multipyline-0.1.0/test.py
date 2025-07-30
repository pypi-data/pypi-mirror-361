# from multipyline import multipyline, multipyline_inner
#
# inner_text = '''
#     Inner line 1
#         Offset inner line 2
#     Inner line 3
# '''
#
# result = multipyline(f'''
#     Outer line 1:
#         {multipyline_inner(inner_text, " " * 8)}
#
#         > Outer line 2:
#         >
#         {multipyline_inner(inner_text, " " * 8 + "> ")}
# ''')
# print(result)

from multipyline import multipyline_format

func_impl = '''
    # Inner part
    if (x > 0):
        print('Another line')
'''

result = multipyline_format(
    '''
    def fun(x: int):
        print('Outer part')
        {}
    ''',
    func_impl,
)

print(result)