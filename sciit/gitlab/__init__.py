"""
@issue gitlab integration
@title Create an integration with gitlab using webhooks
@description
    The webservice should be able to receive JSON payloads from gitlab.
    Essentially, the gitlab webhook will trigger an HTTP request to this
    webservice it will then make another HTTP request back to the gitlab
    api that will create the commit for the issue or issue change and make 
    changes to the source code file where appropriate. 
    
    Then when we pull to our local machine the local issue repository 
    objects can be created and continue to work as designed.

    for future: add the ability for comments
"""