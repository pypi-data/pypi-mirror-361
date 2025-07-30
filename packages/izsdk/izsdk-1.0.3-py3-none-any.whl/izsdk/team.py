from typing import List, Optional
from . import request_pb2 as request
from .connectionPool import get_connection_pool


class Team:
    def __init__(self, name: str, roles: List[str]):
        self._name = name
        self._roles = roles

    def get_name(self) -> str:
        return self._name

    def get_roles(self) -> List[str]:
        return self._roles

    @staticmethod
    async def add_team(name: str, roles: List[str]):
        add_team = request.AddTeam(name=name, roles=roles)
        req = request.Request(addTeam=add_team)
        pool = get_connection_pool()
        resp = await pool.send_and_receive(req)

        if not resp.HasField("addTeam") or resp.addTeam.status != 0:
            raise Exception(resp.addTeam.message or "Failed to add team")

    @staticmethod
    async def remove_team(name: str):
        remove_team = request.RemoveTeam(name=name)
        req = request.Request(removeTeam=remove_team)
        pool = get_connection_pool()
        resp = await pool.send_and_receive(req)

        if not resp.HasField("removeTeam") or resp.removeTeam.status != 0:
            raise Exception(resp.removeTeam.message or "Failed to remove team")

    @staticmethod
    async def update_team(name: str, roles: List[str]):
        update_team = request.UpdateTeam(name=name, roles=roles)
        req = request.Request(updateTeam=update_team)
        pool = get_connection_pool()
        resp = await pool.send_and_receive(req)

        if not resp.HasField("updateTeam") or resp.updateTeam.status != 0:
            raise Exception(resp.updateTeam.message or "Failed to update team")

    @staticmethod
    async def get_team(name: str) -> "Team":
        get_team = request.GetTeam(name=name)
        req = request.Request(getTeam=get_team)
        pool = get_connection_pool()
        resp = await pool.send_and_receive(req)

        if not resp.HasField("getTeam") or resp.getTeam.status != 0:
            raise Exception(resp.getTeam.message or "Failed to get team")

        if not resp.getTeam.team:
            raise Exception("No team data returned")

        team_data = request.Team()
        team_data.ParseFromString(resp.getTeam.team)
        return Team(team_data.name, list(team_data.roles))

    @staticmethod
    async def list_team_names() -> List[str]:
        list_teams = request.ListTeams()
        req = request.Request(listTeams=list_teams)
        pool = get_connection_pool()
        resp = await pool.send_and_receive(req)

        if not resp.HasField("listTeams") or resp.listTeams.status != 0:
            raise Exception(resp.listTeams.message or "List teams failed")

        return list(resp.listTeams.teams)

    @staticmethod
    async def list_teams() -> List["Team"]:
        list_teams = request.ListTeams()
        req = request.Request(listTeams=list_teams)
        pool = get_connection_pool()
        resp = await pool.send_and_receive(req)

        if not resp.HasField("listTeams") or resp.listTeams.status != 0:
            raise Exception(resp.listTeams.message or "List teams failed")

        team_names = list(resp.listTeams.teams)
        teams: List[Team] = []
        for team_name in team_names:
            team = await Team.get_team(team_name)
            teams.append(team)

        return teams
    


