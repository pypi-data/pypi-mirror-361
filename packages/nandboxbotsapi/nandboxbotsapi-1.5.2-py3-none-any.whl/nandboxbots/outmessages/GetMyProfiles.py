from nandboxbots.outmessages.OutMessage import OutMessage


class GetMyProfiles(OutMessage):
    def __init__(self):
        self.method = "getMyProfiles"
        