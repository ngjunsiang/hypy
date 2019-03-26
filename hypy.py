# -*- coding: utf-8 -*-

import requests

def debug_print(func_name,response):
    """Prints useful information for each request from its response"""
    print(f"<{func_name}> {response.request.method} URL: {response.url}")

class HypothesisAPI(object):
    url: None
    user: None
    name: None
    def __init__(self, developerAPIKey=None, authority="hypothes.is"):
        self._ss = requests.Session()
        self._ss.headers.update({'Accept': 'application/json'})
        self.authority = authority
        self.developerAPIKey = developerAPIKey
        profile = self.profile()
        try:
            self.user = profile["userid"].replace("acct:","").replace("@"+self.authority,"")
            self.name = profile["user_info"]["display_name"]
        except AttributeError: #e.g. if userid = None
            print("Authentication error, no user found for developerAPIKey.")

    @property
    def authority(self):
        return self._authority

    @authority.setter
    def authority(self, authority):
        self._authority = authority
        self.url = f"https://{self.authority}/api"

    @property
    def developerAPIKey(self):
        return self._developerAPIKey

    @developerAPIKey.setter
    def developerAPIKey(self,developerAPIKey):
        self._developerAPIKey = developerAPIKey
        auth_header = None if developerAPIKey is None else 'Bearer '+developerAPIKey
        self._ss.headers.update({'Authorization': auth_header}) #removes header key if value is None

    def url_for(self, *args):
        """URL helper to form full URL for methods."""
        request_url = self.url
        for arg in args:
            request_url = "/".join([request_url,arg])
        return request_url

    """
    API methods
    """
    def profile(self): #Responses: 200
        """Return profile of authenticated user.

        This can either be accessed with an API key, in which case it will show the
        authenticated user's profile, or without, in which case it will show infor-
        mation for a logged-out profile, including only public groups for the cur-
        rent authority.

        Args:
            None

        Returns:
            json response from hypothes.is

        Examples:
            >>> h = HypothesisAPI(developerAPIKey)
            >>> p = h.profile
            >>> print p['userid']
        """
        response = self._ss.get(self.url_for("profile"))
        return response.json()

    def get_links(self):
        """URL templates for generating URLs for HTML pages."""
        response = self._ss.get(self.url_for("links"))
        debug_print(self.__class__.__name__,response)
        return response.json()

class AnnotationAPI(HypothesisAPI):
    def __init__(self, developerAPIKey=None, authority="hypothes.is"):
        super().__init__(developerAPIKey, authority)

    def get(self, id: str): #Responses: 200,404
        """
        Fetch an annotation.

        Keyword arguments:
        id -- <str> ID of annotation to return.
        """
        try:
            response = self._ss.get(self.url_for("annotations",id))
            debug_print(self.__class__.__name__,response)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        else:
            return response.json()

    def search(self, **kwargs): #Responses: 200
        """
        Search for annotations.

        Keyword arguments:
        limit=<int> [0 .. 200](default 20)
            The maximum number of annotations to return.
        offset=<int> [0 .. 9800](default 0)
            The number of initial annotations to skip.
            This is used for pagination. Not suitable for paging through thousands
            of annotations-search_after should be used instead.
        sort=<str> [Enum:"created" "updated" "group" "id" "user" ](default "updated")
            The field by which annotations should be sorted.
        search_after=<str>
            Returns results after the annotation whose sort field
            has this value. If specifying a date use the format
            yyyy-MM-dd'T'HH:mm:ss.SSX or time in miliseconds since the epoch.
            This is used for iteration through large collections of results.
        order=<str> [Enum:"asc" "desc"](default "desc")
            The order in which the results should be sorted.
        uri=<str>
            Limit the results to annotations matching the specific URI or equivalent URIs.
            URI can be a URL (a web page address) or a URN representing another kind of
            resource such as DOI (Digital Object Identifier) or a PDF fingerprint.
        uri.parts=<str>
            Limit the results to annotations containing the given keyword in the URL.
        url=<str>
            Alias of `uri`.
        wildcard_uri=<str>
            Limit the results to annotations matching the wildcard URI. URI can be a URL (a web page address) or a URN representing another kind of resource such as DOI (Digital Object Identifier) or a PDF fingerprint.
            `*` will match any character sequence (including an empty one), and a `_` will match any single character. Wildcards are only permitted within the path and query parts of the URI.
            Escaping wildcards is not supported.

            Examples of valid uris: http://foo.com/* urn:x-pdf:* file://localhost/_bc.pdf
            Examples of invalid uris: *foo.com u_n:* file://* http://foo.com*

            This feature is experimental and the API may change.
        user=<str>
            Limit the results to annotations made by the specified user.
        group=<str>
            Limit the results to annotations made in the specified group.
        tag=<str>
            Limit the results to annotations tagged with the specified value.
        tags=<str>
            Alias of `tag`.
        any=<str>
            Limit the results to annotations whose quote, tags, text or url fields
            contain this keyword.
        group=<str>
            Limit the results to this group of annotations.
        quote=<str>
            Limit the results to annotations that contain this text
            inside the text that was annotated.
        references=<str>
            Returns annotations that are replies to this parent annotation id.
        text=<str>
            Limit the results to annotations that contain this text in their textual body.
        """
        response = self._ss.get(self.url_for("search"),json=kwargs)
        debug_print(self.__class__.__name__,response)
        return response.json()

    def list(self, **kwargs):
        response = self.search(user=self.user, **kwargs)
        return response

    def create(self, **kwargs): #Responses: 200,400
        """
        Create an annotation.

        Keyword arguments:
        group=<str>
        permissions=<object (Permissions)>
        {
          "read": <list userid>
          "admin": <list userid>
          "update": <list userid>
          "delete": <list userid>
        }
        references=<list of str>
        tags=<list of str>
        target=<list>
        [
          selector=<list>
          [
            type=<str>(required)
          ]
        ]
        text=<str>
        uri=<str>
        """
        try:
            response = self._ss.post(self.url_for("annotations"),json=kwargs)
            debug_print(self.__class__.__name__,response)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        return response.json()

    def update(self, id, **kwargs): #200, 400, 404
        """
        Update an existing annotation.

        Keyword arguments:
        annot_id -- <str> ID of annotation to return.
        group: <str>
        permissions: <object (Permissions)>
        references: <list of str>
        tags: <list of str>
        target: <list>
                [
                  selector: <list>
                  [
                    type: <str>(required)
                  ]
                ]
        text: <str>
        uri: <str>
        """

        try:
            response = self._ss.patch(self.url_for("annotations",id),json=kwargs)
            debug_print(self.__class__.__name__,response)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        return response.json()

    def delete(self, annot_id): #200, 404
        """
        Delete an annotation.

        Keyword arguments:
        annot_id -- <str>(required) ID of annotation to delete.
        """
        try:
            response = self._ss.delete(self.url_for("annotations",annot_id))
            debug_print(self.__class__.__name__,response)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        return response.json()
