import SEAScope.upload

with SEAScope.upload.connect('localhost', 11155) as link:
    SEAScope.upload.select_variable_by_id(link, 2, 1, 1, True, False)

    SEAScope.upload.select_variable_by_label(link, 'Sentinel-3 OLCI', 'Oa09e',
                                             True, True)
