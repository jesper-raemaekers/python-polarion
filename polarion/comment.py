class Comment:
    @staticmethod
    def add_comment(service, parent, title, comment):
        """
        Adds a comment to a workitem, document or test run or reply to an existing comment.

        Throws an exception if the function is disabled in Polarion.

        :param service: Zeep service object
        :param title: Title of the comment (will be None for a reply)
        :param comment: The comment, may contain html
        :param parent: A parent comment, if none provided it's a root comment.
        :return: URI of new comment
        """
        if hasattr(service, 'addComment'):
            content = {
                'type': 'text/html',
                'content': comment,
                'contentLossy': False
            }
            return service.addComment(parent, title, content)
        else:
            raise Exception("addComment binding not found in Tracker Service. Adding comments might be disabled.")
