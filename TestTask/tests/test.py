import pytest


@pytest.mark.asyncio
async def test_create_reservation_conflict(async_client):
    # Attempt to create a reservation (error, as the table does not exist)
    response = await async_client.post("/reservations/", json={
        "customer_name": "John Doe",
        "table_id": 1,
        "reservation_time": "2023-10-01T12:00:00",
        "duration_minutes": 60
    })
    assert response.status_code == 404  # Table does not exist

    # Create a table
    response = await async_client.post("/tables/", json={
        "name": "Table 1",
        "seats": 4,
        "location": "Window"
    })
    assert response.status_code == 200

    # Create the first reservation
    response = await async_client.post("/reservations/", json={
        "customer_name": "John Doe",
        "table_id": 1,
        "reservation_time": "2023-10-01T12:00:00",
        "duration_minutes": 60
    })
    assert response.status_code == 200

    # Attempt to create a conflicting reservation
    response = await async_client.post("/reservations/", json={
        "customer_name": "Jane Doe",
        "table_id": 1,
        "reservation_time": "2023-10-01T12:30:00",
        "duration_minutes": 60
    })
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_table(async_client):
    # Create a table
    response = await async_client.post("/tables/", json={
        "name": "Table 1",
        "seats": 4,
        "location": "Window"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Table 1"

    # Check for duplicate table creation
    response = await async_client.post("/tables/", json={
        "name": "Table 1",
        "seats": 4,
        "location": "Window"
    })
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_tables(async_client):
    # Create multiple tables
    for i in range(3):
        response = await async_client.post("/tables/", json={
            "name": f"Table {i + 1}",
            "seats": 4,
            "location": "Window"
        })
        assert response.status_code == 200

    # Retrieve the list of tables
    response = await async_client.get("/tables/")
    assert response.status_code == 200
    tables = response.json()
    assert len(tables) == 3
    assert tables[0]["name"] == "Table 1"
    assert tables[1]["name"] == "Table 2"
    assert tables[2]["name"] == "Table 3"