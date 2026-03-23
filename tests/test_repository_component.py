import os
import tempfile
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db import Base
from app.repository import StudentRepository
from app.models import Student

@pytest.fixture(scope="function")
def session():
    db_fd, db_path = tempfile.mkstemp()
    engine = create_engine(f"sqlite:///{db_path}", echo=False, future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()  
        os.close(db_fd)
        os.unlink(db_path)

@pytest.fixture(scope="function")
def repo(session):
    return StudentRepository(session)

def test_create_student(repo):
    student = repo.create(name="John Doe", email="john@example.com")
    assert student.id is not None
    assert student.name == "John Doe"
    assert student.email == "john@example.com"

def test_get_all_students(repo):
    repo.create(name="Alice", email="alice@example.com")
    repo.create(name="Bob", email="bob@example.com")
    students = repo.get_all()
    assert len(students) == 2
    assert students[0].name == "Alice"
    assert students[1].name == "Bob"

def test_get_by_id(repo):
    student = repo.create(name="Charlie", email="charlie@example.com")
    found = repo.get_by_id(student.id)
    assert found is not None
    assert found.name == "Charlie"
    assert found.email == "charlie@example.com"

def test_update_student(repo):
    student = repo.create(name="Dave", email="dave@example.com")
    updated = repo.update(student.id, name="David", email="david@example.com")
    assert updated is not None
    assert updated.name == "David"
    assert updated.email == "david@example.com"

def test_delete_student(repo):
    student = repo.create(name="Eve", email="eve@example.com")
    deleted = repo.delete(student.id)
    assert deleted is True
    assert repo.get_by_id(student.id) is None
