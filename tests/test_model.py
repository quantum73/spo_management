from app.models import Title


def test_create_title(database):
    title_name = "title #1"
    title_obj = Title(name=title_name)
    database.session.add(title_obj)
    database.session.commit()

    assert database.session.query(Title).count() == 1
    title_obj_from_db = database.session.query(Title).all()[0]
    assert title_obj_from_db.name == title_name
