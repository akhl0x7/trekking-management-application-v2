def test_unassigned_staff_cannot_manage_trek(client, app):
    from app.extensions import db
    from app.models import StaffProfile, User, UserRole, UserStatus
    with app.app_context():
        user = User(email="otherstaff@test.local", name="Other Staff", role=UserRole.STAFF, status=UserStatus.ACTIVE)
        user.set_password("OtherStaff@12345")
        db.session.add(user)
        db.session.flush()
        db.session.add(StaffProfile(user_id=user.id, employee_id="S2"))
        db.session.commit()
    client.post("/api/v1/auth/login", json={"email": "otherstaff@test.local", "password": "OtherStaff@12345"})
    response = client.patch("/api/v1/staff/treks/1", json={"available_slots": 1})
    assert response.status_code == 403
