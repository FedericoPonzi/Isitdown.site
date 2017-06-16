# Isitdown.site
 * The user should be able to input an ip address, or a website in order to check if it's online
  * Since it's a website, it makes sense to send an http request.
 * It must be FAST As hell: minified, few css.
 * It must be possible to access a site using the url scheme: isitdown.site/{site url}
   * Bonus for isitdown.site/api/{site url}
   * The requests should be logged in order to prevent abuse, and should flush old requests.

# long todo:
 * Support multi-language
 * Add database

# longlong todo:
 * fallback senza javascript

# Connections limits
The site should limit the number check to a host. In order to do this, it should


# Db:
id datetime ip host
