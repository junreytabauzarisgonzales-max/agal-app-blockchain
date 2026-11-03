import re
import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import func, select

from app.admin.listing import DEFAULT_PER_PAGE, ListQuery, Page, parse
from app.admin.resources import RESOURCES
from app.models.enums import BatchStatus, CustodyEventType, OnChainStatus, UserRole
from app.models.message import Message
from app.models.user import User
from tests.test_admin_resources import (
    add_batch,
    add_event,
    add_price,
    add_user,
)


def names_in(html: str) -> list[str]:
    """The row-link / user names visible in list cells, in page order."""
    return re.findall(r'<td>\s*<a class="row-link" href="/admin/users/[^"]+">([^<]+)</a>', html)


def rows_in(html: str) -> int:
    return html.count("<tr>") - 1


@pytest.fixture
def people(db_session_factory):
    with db_session_factory() as s:
        users = [
            add_user(s, "Ana Farmer", UserRole.FARMER, "ana@example.com"),
            add_user(s, "Ben Buyer", UserRole.BUYER, "ben@example.com"),
            add_user(s, "Cara Supplier", UserRole.SUPPLIER, "cara@example.com", active=False),
            add_user(s, "Dan Farmer", UserRole.FARMER, "dan@example.com"),
        ]
        users[0].municipality = "Bongao"
        users[1].municipality = "Sitangkai"
        users[3].municipality = "Bongao"
        users[3].phone_number = "0917-555-0101"
        for i, u in enumerate(users):
            u.created_at = datetime(2026, 9, 10 + i, 12, 0, tzinfo=timezone.utc)
        s.commit()
        return {u.full_name: u.id for u in users}


# --- ListQuery unit tests (no database) ------------------------------------------------

def q(key="users", **params) -> ListQuery:
    return parse(RESOURCES[key], params)


def test_parse_drops_unknown_and_malformed_values():
    lq = q(role="admin", status="maybe", **{"from": "not-a-date", "to": "2026-13-45"}, sort="hashed_password", dir="sideways",
           page="-4", per_page="9999", bogus="1")
    assert lq.filters == {}
    assert lq.sort is None and lq.direction == "asc"
    assert lq.page == 1 and lq.per_page == DEFAULT_PER_PAGE


def test_parse_accepts_valid_values():
    lq = q(q="  ana  ", role="farmer", status="0", **{"from": "2026-09-01"}, sort="email", dir="desc", page="3", per_page="50")
    assert lq.q == "ana"
    assert lq.filters == {"role": "farmer", "status": "0", "from": "2026-09-01"}
    assert (lq.sort, lq.direction, lq.page, lq.per_page) == ("email", "desc", 3, 50)


def test_search_term_is_length_capped():
    assert len(q(q="x" * 500).q) == 100


def test_only_sortable_list_columns_can_be_sorted():
    assert q(sort="full_name").sort == "full_name"
    for not_sortable in ("id", "hashed_password", "phone_number", "nonexistent", "1; DROP TABLE users"):
        assert q(sort=not_sortable).sort is None
    assert q("batches", sort="farmer_id").sort is None  # foreign keys have no useful order


def test_qs_preserves_state_and_resets_the_page():
    lq = q(q="ana", role="farmer", sort="email", dir="desc", per_page="50", page="4")
    assert "page=4" in lq.qs(page=4)
    changed = lq.qs(role="buyer")
    assert "role=buyer" in changed and "q=ana" in changed and "sort=email" in changed and "per_page=50" in changed
    assert not re.search(r"(?<!per_)page=", changed)  # any change other than the page returns to page 1
    assert "q=" not in lq.qs(q=None)
    assert lq.qs_clear() == "?sort=email&dir=desc&per_page=50"


def test_qs_url_encodes_the_search_term():
    assert q(q="a&b=c #x").qs() == "?q=a%26b%3Dc+%23x"


def test_sort_link_toggles_direction():
    assert "dir=asc" in q().sort_qs("email")
    assert "dir=desc" in q(sort="email", dir="asc").sort_qs("email")
    assert "dir=asc" in q(sort="email", dir="desc").sort_qs("email")


def test_chips_describe_and_can_remove_each_filter():
    chips = q(q="ana", role="farmer", status="1").chips()
    assert [(c.label, c.value) for c in chips] == [("Search", "“ana”"), ("Role", "Farmer"), ("Status", "Active")]
    assert "role=" not in chips[1].remove_qs and "q=ana" in chips[1].remove_qs


def test_page_clamping():
    assert Page(99, 25, 30).clamped().number == 2
    assert Page(0, 25, 30).clamped().number == 1
    assert Page(1, 25, 0).clamped().pages == 1


def test_listquery_never_puts_input_in_sql_text():
    lq = q(q="'; DROP TABLE users; --", sort="full_name")
    stmt = str(lq.ordered(lq.where(select(User))).compile(compile_kwargs={"literal_binds": False}))
    assert "DROP TABLE" not in stmt


# --- search ---------------------------------------------------------------------------------

def test_search_matches_name_email_municipality_and_phone_case_insensitively(admin_client, people):
    assert names_in(admin_client.get("/admin/users?q=ANA").text) == ["Ana Farmer"]
    assert names_in(admin_client.get("/admin/users?q=ben@example").text) == ["Ben Buyer"]
    assert set(names_in(admin_client.get("/admin/users?q=bongao").text)) == {"Ana Farmer", "Dan Farmer"}
    assert names_in(admin_client.get("/admin/users?q=555-0101").text) == ["Dan Farmer"]


def test_search_wildcards_are_literal(admin_client, people):
    for term in ("%", "_", "%%", "a%r", "\\"):
        html = admin_client.get("/admin/users", params={"q": term}).text
        assert "No matching users" in html, term


def test_search_with_no_results_shows_a_clearable_empty_state(admin_client, people):
    html = admin_client.get("/admin/users?q=zzzz").text
    assert "No matching users" in html
    assert "Clear search and filters" in html
    assert "No users yet" not in html  # that message is for a genuinely empty table


def test_search_input_is_escaped_in_the_page(admin_client, people):
    html = admin_client.get("/admin/users", params={"q": '"><script>alert(1)</script>'}).text
    assert "<script>alert(1)" not in html


def test_injection_attempts_are_harmless(admin_client, people, db_session_factory):
    for params in ({"q": "'; DROP TABLE users; --"}, {"sort": "full_name; DROP TABLE users"}, {"role": "farmer' OR '1'='1"},
                   {"from": "2026-01-01' OR 1=1 --"}):
        assert admin_client.get("/admin/users", params=params).status_code == 200
    with db_session_factory() as s:
        assert s.scalar(select(func.count()).select_from(User)) == 4


def test_price_search_covers_notes_and_the_poster(admin_client, db_session_factory):
    with db_session_factory() as s:
        sam = add_user(s, "Sam Supplier", UserRole.SUPPLIER)
        other = add_user(s, "Olive Buyer", UserRole.BUYER)
        add_price(s, sam, "Kappaphycus")
        add_price(s, other, "Eucheuma")
        s.commit()
    assert rows_in(admin_client.get("/admin/prices?q=eucheuma").text) == 1
    assert rows_in(admin_client.get("/admin/prices?q=grade+A").text) == 2  # notes: "dry, grade A"
    by_poster = admin_client.get("/admin/prices?q=olive").text
    assert rows_in(by_poster) == 1 and "Eucheuma" in by_poster


def test_batch_and_event_ids_are_searchable_by_prefix(admin_client, db_session_factory):
    with db_session_factory() as s:
        ana = add_user(s)
        b1, b2 = add_batch(s, ana), add_batch(s, ana)
        e1 = add_event(s, b1, ana)
        add_event(s, b2, ana)
        s.commit()
        b1_id, e1_id = str(b1.id), str(e1.id)

    assert f'title="{b1_id}"' in admin_client.get(f"/admin/batches?q={b1_id[:8]}").text
    assert rows_in(admin_client.get(f"/admin/batches?q={b1_id[:8]}").text) == 1
    assert rows_in(admin_client.get(f"/admin/batches?q={b1_id}").text) == 1  # full dashed id
    assert rows_in(admin_client.get(f"/admin/events?q={e1_id[:8]}").text) == 1
    assert rows_in(admin_client.get(f"/admin/events?q={b1_id[:8]}").text) == 1  # events by their batch id
    assert rows_in(admin_client.get("/admin/events?q=ana").text) == 2  # by actor name


def test_message_bodies_are_never_searchable(admin_client, db_session_factory):
    with db_session_factory() as s:
        a, b = add_user(s), add_user(s, "Sam Supplier", UserRole.SUPPLIER)
        s.add(Message(id=uuid.uuid4(), sender_id=a.id, recipient_id=b.id, body="the secret rendezvous", occurred_at=datetime.now(timezone.utc)))
        s.commit()
    assert "No matching messages" in admin_client.get("/admin/messages?q=rendezvous").text
    assert rows_in(admin_client.get("/admin/messages?q=sam").text) == 1  # sender/recipient names do work


# --- filters -----------------------------------------------------------------------------------

def test_user_filters(admin_client, people):
    assert set(names_in(admin_client.get("/admin/users?role=farmer").text)) == {"Ana Farmer", "Dan Farmer"}
    assert names_in(admin_client.get("/admin/users?status=0").text) == ["Cara Supplier"]
    assert len(names_in(admin_client.get("/admin/users?status=1").text)) == 3


def test_filters_combine_with_search(admin_client, people):
    assert names_in(admin_client.get("/admin/users?role=farmer&q=dan").text) == ["Dan Farmer"]
    assert "No matching" in admin_client.get("/admin/users?role=buyer&q=dan").text


def test_date_range_is_inclusive_of_the_end_day(admin_client, people):
    # Joined 2026-09-10 (Ana), 11 (Ben), 12 (Cara), 13 (Dan), all at noon UTC.
    assert set(names_in(admin_client.get("/admin/users?from=2026-09-11&to=2026-09-12").text)) == {"Ben Buyer", "Cara Supplier"}
    assert names_in(admin_client.get("/admin/users?to=2026-09-10").text) == ["Ana Farmer"]
    assert names_in(admin_client.get("/admin/users?from=2026-09-13").text) == ["Dan Farmer"]
    assert "No matching" in admin_client.get("/admin/users?from=2027-01-01").text


def test_price_date_filter_uses_plain_dates(admin_client, db_session_factory):
    with db_session_factory() as s:
        sam = add_user(s, "Sam Supplier", UserRole.SUPPLIER)
        add_price(s, sam)  # effective 2026-09-18
        s.commit()
    assert rows_in(admin_client.get("/admin/prices?from=2026-09-18&to=2026-09-18").text) == 1
    assert "No matching" in admin_client.get("/admin/prices?from=2026-09-19").text
    assert "No matching" in admin_client.get("/admin/prices?to=2026-09-17").text


def test_batch_event_and_message_filters(admin_client, db_session_factory):
    with db_session_factory() as s:
        ana, sam = add_user(s), add_user(s, "Sam Supplier", UserRole.SUPPLIER)
        b1, b2 = add_batch(s, ana), add_batch(s, ana)
        b2.status = BatchStatus.EXPORTED
        e1 = add_event(s, b1, ana, OnChainStatus.FAILED)
        e1.event_type = CustodyEventType.DRYING_STARTED
        add_event(s, b1, sam, OnChainStatus.ANCHORED)
        now = datetime.now(timezone.utc)
        s.add(Message(id=uuid.uuid4(), sender_id=ana.id, recipient_id=sam.id, body="x", occurred_at=now, read_at=now))
        s.add(Message(id=uuid.uuid4(), sender_id=sam.id, recipient_id=ana.id, body="y", occurred_at=now))
        s.commit()

    assert rows_in(admin_client.get("/admin/batches?status=exported").text) == 1
    assert rows_in(admin_client.get("/admin/events?chain=failed").text) == 1
    assert rows_in(admin_client.get("/admin/events?type=drying_started").text) == 1
    assert rows_in(admin_client.get("/admin/events?role=supplier").text) == 1
    assert rows_in(admin_client.get("/admin/messages?state=yes").text) == 1
    assert rows_in(admin_client.get("/admin/messages?state=no").text) == 1


def test_relationship_filters_by_uuid(admin_client, db_session_factory):
    with db_session_factory() as s:
        ana, ben = add_user(s), add_user(s, "Ben Buyer", UserRole.BUYER)
        add_batch(s, ana)
        add_batch(s, ana)
        b3 = add_batch(s, ben)
        add_event(s, b3, ben)
        now = datetime.now(timezone.utc)
        s.add(Message(id=uuid.uuid4(), sender_id=ana.id, recipient_id=ben.id, body="x", occurred_at=now))
        s.commit()
        ana_id, ben_id, b3_id = ana.id, ben.id, b3.id

    assert rows_in(admin_client.get(f"/admin/batches?farmer={ana_id}").text) == 2
    assert rows_in(admin_client.get(f"/admin/batches?farmer={ben_id}").text) == 1
    assert rows_in(admin_client.get(f"/admin/events?batch={b3_id}").text) == 1
    assert "No matching" in admin_client.get(f"/admin/events?actor={ana_id}").text  # Ana recorded no events
    assert rows_in(admin_client.get(f"/admin/events?actor={ben_id}").text) == 1
    # A participant filter matches either side of the conversation.
    assert rows_in(admin_client.get(f"/admin/messages?user={ana_id}").text) == 1
    assert rows_in(admin_client.get(f"/admin/messages?user={ben_id}").text) == 1
    # Malformed uuids are ignored rather than erroring.
    assert admin_client.get("/admin/batches?farmer=not-a-uuid").status_code == 200


def test_detail_pages_link_to_filtered_lists(admin_client, db_session_factory):
    with db_session_factory() as s:
        ana = add_user(s)
        for _ in range(3):
            add_batch(s, ana)
        s.commit()
        ana_id = ana.id
    html = admin_client.get(f"/admin/users/{ana_id}").text
    assert f'href="/admin/batches?farmer={ana_id}"' in html
    assert f'href="/admin/batches?holder={ana_id}"' in html
    assert f'href="/admin/messages?user={ana_id}"' not in html  # no messages, so nothing to view
    followed = admin_client.get(f"/admin/batches?farmer={ana_id}").text
    assert "Farmer:" in followed  # shown as an applied filter chip


# --- sorting -----------------------------------------------------------------------------------

def test_sorting_ascending_and_descending(admin_client, people):
    asc = names_in(admin_client.get("/admin/users?sort=full_name&dir=asc").text)
    assert asc == ["Ana Farmer", "Ben Buyer", "Cara Supplier", "Dan Farmer"]
    assert names_in(admin_client.get("/admin/users?sort=full_name&dir=desc").text) == asc[::-1]
    assert names_in(admin_client.get("/admin/users?sort=email&dir=desc").text)[0] == "Dan Farmer"


def test_default_order_is_newest_first_and_bad_sort_falls_back(admin_client, people):
    default = names_in(admin_client.get("/admin/users").text)
    assert default == ["Dan Farmer", "Cara Supplier", "Ben Buyer", "Ana Farmer"]
    assert names_in(admin_client.get("/admin/users?sort=hashed_password").text) == default


def test_null_values_sort_last_in_both_directions(admin_client, people):
    # Only Ana, Ben and Dan have a municipality; Cara's is NULL.
    for direction in ("asc", "desc"):
        assert names_in(admin_client.get(f"/admin/users?sort=municipality&dir={direction}").text)[-1] == "Cara Supplier"


def test_headers_show_sort_links_and_state(admin_client, people):
    html = admin_client.get("/admin/users?sort=full_name&dir=asc").text
    assert 'aria-sort="ascending"' in html
    assert 'href="/admin/users?sort=full_name&amp;dir=desc"' in html  # clicking again reverses
    assert "&#9650;" in html
    assert "&amp;#9650;" not in html  # the arrow entity must not be double-escaped
    assert 'href="/admin/users?sort=phone_number' not in html  # detail-only column: no header
    batches = admin_client.get("/admin/batches").text
    assert "sort=farmer_id" not in batches  # foreign keys are not sortable


# --- pagination & page size -------------------------------------------------------------------------

@pytest.fixture
def many(db_session_factory):
    with db_session_factory() as s:
        for i in range(30):
            add_user(s, f"Person {i:02d}", UserRole.FARMER if i % 2 else UserRole.BUYER, f"p{i}@example.com")
        s.commit()


def test_page_size_choices(admin_client, many):
    assert rows_in(admin_client.get("/admin/users?per_page=10").text) == 10
    assert rows_in(admin_client.get("/admin/users?per_page=50").text) == 30
    assert rows_in(admin_client.get("/admin/users?per_page=7").text) == DEFAULT_PER_PAGE  # not an allowed size


def test_pagination_links_keep_search_filters_and_sort(admin_client, many):
    html = admin_client.get("/admin/users?role=farmer&sort=full_name&dir=asc&per_page=10").text
    assert "of 15 matching" in html
    next_link = re.search(r'href="([^"]+)" rel="next"', html).group(1).replace("&amp;", "&")
    assert "role=farmer" in next_link and "sort=full_name" in next_link and "per_page=10" in next_link and "page=2" in next_link
    second = admin_client.get(next_link).text
    assert rows_in(second) == 5
    assert "Page 2 of 2" in second


def test_paging_through_a_sorted_list_has_no_duplicates_or_gaps(admin_client, many):
    seen = []
    for page in (1, 2, 3):
        seen += names_in(admin_client.get(f"/admin/users?sort=full_name&per_page=10&page={page}").text)
    assert seen == sorted(seen) and len(set(seen)) == 30


def test_page_past_the_end_after_filtering_is_clamped(admin_client, many):
    html = admin_client.get("/admin/users?role=farmer&page=99").text
    assert "Page 1 of 1" not in html  # 15 results fit on one default page, so no pager at all
    assert rows_in(html) == 15


def test_apply_form_keeps_hidden_state(admin_client, many):
    html = admin_client.get("/admin/users?sort=email&dir=desc").text
    assert 'name="sort" value="email"' in html and 'name="dir" value="desc"' in html


def test_every_resource_list_renders_with_every_filter_at_once(admin_client, people):
    params = {"q": "a", "from": "2020-01-01", "to": "2030-01-01", "per_page": "10", "page": "1"}
    for key in RESOURCES:
        assert admin_client.get(f"/admin/{key}", params=params).status_code == 200, key


def test_lists_still_require_login_with_query_strings(client):
    response = client.get("/admin/users?q=ana&role=farmer")
    assert response.status_code == 303 and response.headers["location"] == "/admin/login"


def test_filters_are_all_declared_for_real_columns():
    for res in RESOURCES.values():
        for f in res.filters:
            for name in f.columns:
                assert hasattr(res.model, name), (res.key, f.name, name)
            if f.kind == "enum":
                assert f.enum_cls is not None and f.options
