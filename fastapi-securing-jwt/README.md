## Securing FastAPI with JWT Token-based Authentication

In this tutorial, you'll learn how to secure a FastAPI app by enabling authentication using JSON Web Tokens (JWTs). We'll be using PyJWT to sign, encode, and decode JWT tokens.

## Authentication in FastAPI

Authentication is the process of verifying users before granting them access to secured resources. When a user is authenticated, the user is allowed to access secure resources not open to the public.

We'll be looking at authenticating a FastAPI app with Bearer (or Token-based) authentication, which involves generating security tokens called bearer tokens. The bearer tokens in this case will be JWTs.
