from abc import ABC

from polarion.base.polarion_object import PolarionObject


class Comment:
    def __init__(self, parent: PolarionObject, index: int):
        self.parent = parent
        self.index = index
        self.uri = self.comment.uri

    def __repr__(self):
        return (
            f"<Comment {self.parent.id} #{self.index + 1}>({self.comment.text.content})"
        )

    def __getattr__(self, item):
        # This makes it possible to access the comment attributes directly
        if hasattr(self.comment, item):
            return getattr(self.comment, item)
        raise AttributeError(f"Comment has no attribute {item}")

    @property
    def comment(self):
        if hasattr(self.parent.comments, "Comment"):
            return self.parent.comments.Comment[self.index]
        elif hasattr(self.parent.comments, "ModuleComment"):
            return self.parent.comments.ModuleComment[self.index]
        raise NotImplementedError("Comment object not supported")

    def setCommentTags(self, tags):
        """Sets the tags of a comment.
        Parameters:
        commentURI - The URI of the comment.
        tags - The tags to set.
        """
        tracker = self.parent._polarion.getService("Tracker")
        tracker.setCommentTags(self.uri, tags)

    def setResolved(self, resolved: bool):
        """Sets the state of the comment to "Resolved". Can only be used for root comments.
        Throws:
        RemoteException

        :param resolved: - The new resolved state.
        :type resolved: bool
        """
        tracker = self.parent._polarion.getService("Tracker")
        tracker.setResolvedComment(self.uri, resolved)

    def isResolved(self) -> bool:
        """
        Checks if the comment is in a resolved comments thread.
        :return: True if the comment is in a resolved comments thread, False otherwise.
        :rtype: bool
        """
        tracker = self.parent._polarion.getService("Tracker")
        return tracker.isResolvedComment(self.uri)

    def isReply(self) -> bool:
        # self.comment.
        if self.comment.parentCommentURI is None:
            return False
        return True

    def replies(self):
        """Returns the replies of the comment."""
        answer = []
        if self.comment.childCommentURIs is not None:
            for uri in self.comment.childCommentURIs.SubterraURI:
                for index, subcomment in enumerate(self.parent.comments.Comment):
                    if subcomment.uri == uri:
                        answer.append(Comment(self.parent, index))
            if len(answer) == 0:
                raise NotImplementedError(
                    "This is awkward, it reports replies but there are none. Investigate!"
                )
        return answer



class Comments(PolarionObject, ABC):
    def addComment(self, title, comment, parent=None, type="html"):
        """
        Adds a comment to the workitem.

        Throws an exception if the function is disabled in Polarion.

        :param title: Title of the comment (will be None for a reply)
        :param comment: The comment, may contain html
        :param parent: A parent comment, if none provided it's a root comment.
        """
        service = self._polarion.getService("Tracker")
        if type not in ["html", "plain"]:
            raise Exception("Type must be either html or plain.")
        if hasattr(service, "addComment"):
            if parent is None:
                parent = self.uri
            else:
                # force title to be empty, not allowed for reply comments
                title = None
            content = {
                "type": f"text/{type}",
                "content": comment,
                "contentLossy": False,
            }
            service.addComment(parent, title, content)
            self._reloadFromPolarion()
        else:
            raise Exception(
                "addComment binding not found in Tracker Service. Adding comments might be disabled."
            )

    def getComments(self):
        """
        Returns a list of Comment objects.
        """
        if self.comments is None:
            return []
        if hasattr(self.comments, "Comment"):
            return [Comment(self, index) for index in range(len(self.comments.Comment))]
        elif hasattr(self.comments, "ModuleComment"):
            return [Comment(self, index) for index in range(len(self.comments.ModuleComment))]
