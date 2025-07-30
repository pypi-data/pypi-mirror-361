class LavalinkException(Exception):
    """Base exception for all sonocore errors."""


class AuthorizationFailed(LavalinkException):
    """Raised when the password for a Lavalink node is incorrect."""


class NodeOccupied(LavalinkException):
    """Raised when a node identifier is already in use."""


class NoNodesAvailable(LavalinkException):
    """Raised when there are no available nodes to connect to."""


class PlayerNotConnected(LavalinkException):
    """Raised when an operation is attempted on a player that is not connected."""


class QueueEmpty(LavalinkException):
    """Raised when an operation is attempted on an empty queue."""


class NoResultsFound(LavalinkException):
    """Raised when a search yields no results."""