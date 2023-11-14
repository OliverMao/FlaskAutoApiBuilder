from blueprints.generic import generic_bp


def register(app):
    # 初始化一个空的蓝图列表
    # Initialize an empty list for blueprints
    blueprints = list()

    # 将generic_bp添加到蓝图列表中
    # Append generic_bp to the blueprints list
    # 在此处添加自定义蓝图
    blueprints.append(generic_bp)

    # 将蓝图列表中的所有蓝图添加到应用程序中
    # Add all blueprints in the blueprints list to the app
    app.add_blueprints(blueprints)
    return app
