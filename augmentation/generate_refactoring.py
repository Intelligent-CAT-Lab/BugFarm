from augmentation.refactoring_methods import *


def generate_adversarial(k, code, refactor):
    final_refactor = ''
    function_list = []
    class_name = ''
    vv = 0

    class_list, raw_code =  extract_class(code)

    for class_name in class_list:
        function_list, class_name = extract_function(class_name)

    refac = []
    for code in function_list:
        new_rf = code
        new_refactored_code = code

        for t in range(k):
            
            vv = 0
            
            while new_rf == new_refactored_code and vv <= 20:
                try:
                    vv += 1
                    # print('*' * 50 , refactor , '*' * 50)
                    new_refactored_code = refactor(new_refactored_code)

                except Exception as error:
                    # print('error:\t',error)
                    pass

            new_rf = new_refactored_code

            # print('----------------------------CHANGED THIS TIME:----------------------------------', vv)

        refac.append(new_refactored_code)

    code_body = raw_code.strip() + ' ' + class_name.strip()

    for i in range(len(refac)):
        final_refactor = code_body.replace('vesal'+ str(i), str(refac[i]))
        code_body = final_refactor

    return final_refactor
