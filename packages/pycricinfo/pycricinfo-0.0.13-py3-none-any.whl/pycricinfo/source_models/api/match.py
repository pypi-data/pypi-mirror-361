from typing import Literal, Optional

from pydantic import AliasChoices, BaseModel, Field, computed_field

from pycricinfo.source_models.api.athelete import Athlete
from pycricinfo.source_models.api.common import CCBaseModel, RefMixin
from pycricinfo.source_models.api.match_note import MatchNote
from pycricinfo.source_models.api.official import Official
from pycricinfo.source_models.api.roster import TeamLineup
from pycricinfo.source_models.api.team import TeamWithColorAndLogos
from pycricinfo.source_models.api.venue import Venue


class TeamWicketDetails(CCBaseModel):
    text: str
    short_text: str


class TeamWicket(CCBaseModel):
    details: TeamWicketDetails
    balls_faced: int
    dismissal_card: str
    fours: int
    fow: str
    minutes: Optional[int | str] = None  # TODO: Can be empty string - parse to null in that case
    number: int
    over: float
    runs: int
    short_text: str
    sixes: int
    strike_rate: float


class TeamOver(CCBaseModel):
    number: int
    runs: int
    wicket: list[TeamWicket]


class TeamLinescoreStatistics(CCBaseModel):
    name: str
    overs: list[list[TeamOver]]
    # TODO: Add categories


class PartnershipBatter(CCBaseModel):
    athlete: Athlete
    balls: str|int
    runs: str|int


class InningsState(BaseModel):
    overs: str|float
    runs: str|int
    wickets: str|int


class Partnership(RefMixin, CCBaseModel):
    wicket_number: int
    wicket_name: str
    fow_type: Literal["out", "end of innings"]
    overs: float
    runs: int
    run_rate: float
    start: InningsState
    end: InningsState
    batsmen: list[PartnershipBatter]


class FallOfWicket(RefMixin, CCBaseModel):
    wicket_number: int
    wicket_over: float
    fow_type: Literal["out", "end of innings"]
    runs: int
    runs_scored: int
    balls_faced: int
    athlete: Athlete


class TeamLinescore(CCBaseModel):
    period: int
    wickets: int
    runs: int
    overs: float
    is_batting: bool
    fours: Optional[int] = None
    sixes: Optional[int] = None
    description: str
    target: int
    follow_on: int
    statistics: Optional[TeamLinescoreStatistics]
    partnerships: Optional[list[Partnership]] = None
    fall_of_wicket: Optional[list[FallOfWicket]] = Field(
        default=None,
        validation_alias=AliasChoices("fall_of_wicket", "fow"))


class MatchCompetitor(CCBaseModel):
    id: int
    winner: bool
    team: TeamWithColorAndLogos
    score: str
    linescores: list[TeamLinescore]
    home_or_away: Literal["home", "away"] = Field(validation_alias=AliasChoices("home_or_away", "homeAway"))


class MatchStatus(CCBaseModel):
    summary: str


class MatchCompetiton(CCBaseModel):
    status: MatchStatus
    competitors: list[MatchCompetitor]
    limited_overs: bool


class MatchHeader(CCBaseModel):
    id: int
    name: str
    description: str
    short_name: str
    title: str
    competitions: list[MatchCompetiton]

    @computed_field
    @property
    def summary(self) -> bool:
        return self.competitions[0].status.summary

    @computed_field
    @property
    def competition(self) -> MatchCompetiton:
        return self.competitions[0]

    def get_batting_linescore_for_period(self, period: int) -> tuple[TeamWithColorAndLogos, TeamLinescore]:
        for competitor in self.competition.competitors:
            for linescore in competitor.linescores:
                if linescore.period == period and linescore.is_batting:
                    return competitor.team, linescore


class MatchInfo(BaseModel):
    venue: Venue
    attendance: Optional[int] = None
    officials: list[Official]


class Match(CCBaseModel):
    notes: list[MatchNote]
    game_info: MatchInfo
    # TODO: add debuts
    rosters: list[TeamLineup]
    header: MatchHeader


class MatchBasic(CCBaseModel):
    id: int
    name: str
    description: str
    short_name: str
    short_description: str
    season: RefMixin
    season_type: RefMixin
    # TODO: Add competitions
    venues: list[RefMixin]
    # TODO: links
    # TODO: leagues
