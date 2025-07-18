def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.csv']
    # isCsv = True
    if not ext.lower() in valid_extensions:
        # isCsv = False
        print("****** sorry, not a csv file *****")
        raise ValidationError('Unsupported file extension.')

def validate_file_extension2(value):
    import os
    isCsv = True
    ext = os.path.splitext(value)[1]  # [0] returns path+filename
    valid_extensions = ['.csv']
    if not ext.lower() in valid_extensions:
        isCsv = False
    return isCsv

def validate_file_s3(value):
    import os
    isCsv = True
    # print("xxxxxxxxext = {}".format(str(value).split('.')))
    ext = str(value).split('.')[-1]
    valid_extensions = ['csv']
    if not ext.lower() in valid_extensions:
        isCsv = False
        # print("xxxxxxxxext = {}".format(isCsv))
    return isCsv

def validate_new_data(x):
    isValid = True
    user_id = x.user_id
    # rating = x.rating
    isbn = x.isbn
    # print("xxxxxxxx {}; {}".format(len(user_id), len(list(set(user_id)))))
    if len(isbn) < 10:
        isValid = False
    if len(isbn) != len(list(set(isbn))):
        isValid = False
    if len(list(set(user_id))) != 1:
        isValid = False
    return isValid
