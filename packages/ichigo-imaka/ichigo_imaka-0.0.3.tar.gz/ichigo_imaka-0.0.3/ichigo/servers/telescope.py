"""Communicates with the telescope control system (TCS). This is currently configured \
for IRTF.

TODO:
- retrieve weather data automatically
"""

from ichigo.servers.server import Server


class TelescopeServer(Server):
    """Communicates with the IRTF TCS.
    """
    def __init__(self, alias: str, host_name: str | None = None, jumps: list[str] = []) -> None:
        super().__init__(alias, host_name, jumps=jumps)
    
    def test_t3io(self) -> None:
        """Runs a test script that  nchecks if t3io can be accessed.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.execute("t3io test.t3io")
    
    def offset_rel(self, dra: float, ddec: float) -> None:
        """Applies a relative offset to the RA and Dec.

        Parameters
        ----------
        dra: float
            RA offset in arcseconds. Cannot exceed 30".
        ddec: float
            Dec offset in arcseconds. Cannot exceed 30".
    
        Returns
        -------
        n/a
        """
        assert abs(dra) <= 30, "RA offset must be less than or equal to 30\""
        assert abs(ddec) <= 30, "Dec offset must be less than or equal to 30\""
        self.execute("t3io user.inc " + str(dra) + " " + str(ddec))
    
    def offset_abs(self, dra: float, ddec: float) -> None:
        """Applies an absolute offset to the RA and Dec.

        Parameters
        ----------
        dra: float
            RA offset in arcseconds. Cannot exceed 30".
        ddec: float
            Dec offset in arcseconds. Cannot exceed 30".
    
        Returns
        -------
        n/a
        """
        assert abs(dra) <= 30, "RA offset must be less than or equal to 30\""
        assert abs(ddec) <= 30, "Dec offset must be less than or equal to 30\""
        self.execute("t3io user.set " + str(dra) + " " + str(ddec))

    def nonsidereal_rel(self, rra: float, rdec: float) -> None:
        """Applies a relative change to the current non-sidereal rate.

        Parameters
        ----------
        rra: float
            RA rate in arcseconds/second. Cannot exceed 1"/s.
        rdec: float
            Dec rate in arcseconds/second. Cannot exceed 1"/s.
        
        Returns
        -------
        None
        """
        assert abs(rra) <= 1, "Non-sidereal rate cannot exceed 0.1\"/s"
        assert abs(rdec) <= 1, "Non-sidereal rate cannot exceed 0.1\"/s"
        self.execute("t3io ns.rate " + str(rra) + " " + str(rdec))

    def nonsidereal_abs(self, rra:float, rdec:float) -> None:
        """Sets the non-sidereal rate.

        Parameters
        ----------
        rra: float
            RA rate in arcseconds/second. Cannot exceed 1"/s.
        rdec: float
            Dec rate in arcseconds/second. Cannot exceed 1"/s.
        
        Returns
        -------
        None
        """
        assert abs(rra) <= 1, "Non-sidereal rate cannot exceed 0.1\"/s"
        assert abs(rdec) <= 1, "Non-sidereal rate cannot exceed 0.1\"/s"
        self.execute("t3io ns.rate.inc " + str(rra) + " " + str(rdec))

    def get_weather_data(self):
        """IRTF IQUP, can I get data from MKWC?
        """
        pass