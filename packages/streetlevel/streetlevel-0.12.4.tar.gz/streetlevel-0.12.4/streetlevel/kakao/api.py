from aiohttp import ClientSession
from requests import Session
from ..util import get_json, get_json_async


def build_find_panorama_by_id_request_url(panoid: int) -> str:
    return f"https://rv.map.kakao.com/roadview-search/v2/node/{panoid}?SERVICE=glpano"


def build_find_panoramas_request_url(lat: float, lon: float, radius: int, limit: int) -> str:
    return f"https://rv.map.kakao.com/roadview-search/v2/nodes?" \
           f"PX={lon}&PY={lat}&RAD={radius}&PAGE_SIZE={limit}&INPUT=wgs&TYPE=w&SERVICE=glpano"


def find_panorama_by_id(panoid: int, session: Session = None) -> dict:
    return get_json(build_find_panorama_by_id_request_url(panoid), session)


async def find_panorama_by_id_async(panoid: int, session: ClientSession) -> dict:
    return await get_json_async(build_find_panorama_by_id_request_url(panoid), session)


def find_panoramas(lat: float, lon: float, radius: int, limit: int, session: Session = None) -> dict:
    return get_json(build_find_panoramas_request_url(lat, lon, radius, limit), session)


async def find_panoramas_async(lat: float, lon: float, session: ClientSession, radius: int, limit: int) -> dict:
    return await get_json_async(build_find_panoramas_request_url(lat, lon, radius, limit), session)
