from fastapi.testclient import TestClient

URL = "/api/v1/programs"


def ids(response_json: dict) -> list[int]:
    return [item["id"] for item in response_json["items"]]


def test_list_returns_first_page_with_metadata(client: TestClient) -> None:
    response = client.get(URL)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 12
    assert body["page"] == 1
    assert body["page_size"] == 20
    assert body["total_pages"] == 1
    assert ids(body) == list(range(1, 13))


def test_list_item_has_summary_fields_only(client: TestClient) -> None:
    item = client.get(URL).json()["items"][0]

    assert set(item) == {
        "id",
        "name",
        "summary",
        "category",
        "scope",
        "state",
        "municipality",
    }


def test_pagination_splits_results(client: TestClient) -> None:
    first = client.get(URL, params={"page_size": 5}).json()
    last = client.get(URL, params={"page_size": 5, "page": 3}).json()

    assert ids(first) == [1, 2, 3, 4, 5]
    assert first["total_pages"] == 3
    assert ids(last) == [11, 12]


def test_page_beyond_last_returns_empty_items(client: TestClient) -> None:
    body = client.get(URL, params={"page_size": 5, "page": 10}).json()

    assert body["items"] == []
    assert body["total"] == 12


def test_filter_by_state_includes_national_state_and_municipal(client: TestClient) -> None:
    body = client.get(URL, params={"state": "SP"}).json()

    assert ids(body) == [1, 2, 3, 4, 5, 9, 10, 11]


def test_filter_by_state_is_case_insensitive(client: TestClient) -> None:
    assert ids(client.get(URL, params={"state": "sp"}).json()) == [1, 2, 3, 4, 5, 9, 10, 11]


def test_filter_by_state_without_local_programs_returns_only_national(
    client: TestClient,
) -> None:
    assert ids(client.get(URL, params={"state": "AC"}).json()) == [1, 2, 3]


def test_filter_by_municipality_keeps_national_state_and_that_municipality(
    client: TestClient,
) -> None:
    body = client.get(URL, params={"state": "SP", "municipality": "Campinas"}).json()

    assert ids(body) == [1, 2, 3, 4, 5, 10]


def test_filter_by_municipality_ignores_accents_and_case(client: TestClient) -> None:
    body = client.get(URL, params={"state": "SP", "municipality": "sao paulo"}).json()

    assert 9 in ids(body)
    assert 10 not in ids(body)


def test_filter_by_municipality_requires_state(client: TestClient) -> None:
    response = client.get(URL, params={"municipality": "Campinas"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_filter"


def test_filter_with_unknown_state_is_rejected(client: TestClient) -> None:
    response = client.get(URL, params={"state": "XX"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_filter"


def test_filter_with_malformed_state_is_a_validation_error(client: TestClient) -> None:
    response = client.get(URL, params={"state": "SPP"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_filter_by_category(client: TestClient) -> None:
    assert ids(client.get(URL, params={"category": "educacao"}).json()) == [2, 7, 8, 10]


def test_filter_by_category_combines_with_state(client: TestClient) -> None:
    body = client.get(URL, params={"category": "educacao", "state": "SP"}).json()

    assert ids(body) == [2, 10]


def test_invalid_category_is_rejected(client: TestClient) -> None:
    response = client.get(URL, params={"category": "inexistente"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_text_search_ignores_case_and_accents(client: TestClient) -> None:
    assert ids(client.get(URL, params={"q": "REFEIÇÃO"}).json()) == [9]


def test_text_search_requires_all_words(client: TestClient) -> None:
    assert ids(client.get(URL, params={"q": "cesta alimentos"}).json()) == [4]
    assert ids(client.get(URL, params={"q": "cesta escolar"}).json()) == []


def test_invalid_pagination_parameters_are_rejected(client: TestClient) -> None:
    for params in ({"page": 0}, {"page_size": 0}, {"page_size": 101}):
        response = client.get(URL, params=params)

        assert response.status_code == 422
        assert response.json()["error"]["code"] == "validation_error"


def test_validation_error_lists_details(client: TestClient) -> None:
    error = client.get(URL, params={"page": 0}).json()["error"]

    assert error["details"]
    assert error["details"][0]["loc"] == ["query", "page"]


def test_get_program_detail(client: TestClient) -> None:
    response = client.get(f"{URL}/9")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 9
    assert body["name"].startswith("[FICTÍCIO]")
    assert body["scope"] == "municipal"
    assert body["state"] == "SP"
    assert body["municipality"] == "São Paulo"
    assert isinstance(body["eligibility"], list)
    assert body["official_url"] is None


def test_get_unknown_program_returns_404(client: TestClient) -> None:
    response = client.get(f"{URL}/999")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "not_found", "message": "Programa 999 não encontrado."}
    }


def test_get_program_with_invalid_id_is_rejected(client: TestClient) -> None:
    assert client.get(f"{URL}/0").status_code == 422
    assert client.get(f"{URL}/abc").status_code == 422
