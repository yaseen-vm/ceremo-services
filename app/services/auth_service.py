"""Authentication service."""

from app.repositories.rental_partner_repository import RentalPartnerRepository
from app.contracts.auth_contracts import AuthResponse, AuthData, UserData
from app.utils.security import hash_password, verify_password, generate_token
from app.utils.errors import ValidationError, UnauthorizedError, ConflictError
from app.models.rental_partner import RentalPartner


class AuthService:
    """Service for authentication operations."""

    def __init__(
        self,
        repository: RentalPartnerRepository,
        jwt_secret: str,
        jwt_expiration: int,
        refresh_expiration: int,
        min_password_length: int,
        remember_me_multiplier: int,
    ):
        self.repository = repository
        self.jwt_secret = jwt_secret
        self.jwt_expiration = jwt_expiration
        self.refresh_expiration = refresh_expiration
        self.min_password_length = min_password_length
        self.remember_me_multiplier = remember_me_multiplier

    def sign_up(
        self,
        email: str,
        password: str,
        confirm_password: str,
        first_name: str,
        last_name: str,
        phone: str,
        agree_to_terms: bool,
    ) -> AuthResponse:
        """Register new rental partner."""
        if not agree_to_terms:
            raise ValidationError("You must agree to terms and conditions")

        if password != confirm_password:
            raise ValidationError("Passwords do not match")

        if len(password) < self.min_password_length:
            raise ValidationError(
                f"Password must be at least {self.min_password_length} characters"
            )

        existing = self.repository.find_by_email(email)
        if existing:
            raise ConflictError("Email already exists", "email")

        password_hash = hash_password(password)
        partner = self.repository.create(
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
        )

        return self._create_auth_response(
            partner, "Registration successful", self.jwt_expiration
        )

    def sign_in(self, email: str, password: str, remember_me: bool) -> AuthResponse:
        """Authenticate rental partner."""
        partner = self.repository.find_by_email(email)
        if not partner:
            raise UnauthorizedError("Invalid email or password")

        if not verify_password(password, partner.password_hash):
            raise UnauthorizedError("Invalid email or password")

        expiration = (
            self.jwt_expiration * self.remember_me_multiplier
            if remember_me
            else self.jwt_expiration
        )
        return self._create_auth_response(partner, "Sign in successful", expiration)

    def _create_user_data(self, partner: RentalPartner) -> UserData:
        """Create UserData from RentalPartner."""
        return UserData(
            id=partner.id,
            email=partner.email,
            firstName=partner.first_name,
            lastName=partner.last_name,
            phone=partner.phone,
        )

    def _create_auth_response(
        self, partner: RentalPartner, message: str, token_expiration: int
    ) -> AuthResponse:
        """Create AuthResponse with tokens and user data."""
        token = generate_token(partner.id, self.jwt_secret, token_expiration)
        refresh_token = generate_token(
            partner.id, self.jwt_secret, self.refresh_expiration
        )
        user_data = self._create_user_data(partner)
        auth_data = AuthData(user=user_data, token=token, refreshToken=refresh_token)
        return AuthResponse(data=auth_data, message=message)
