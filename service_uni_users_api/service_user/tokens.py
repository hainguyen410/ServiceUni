from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six


class UserTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, staff, timestamp):
        staff_id = six.text_type(staff.pk)
        ts = six.text_type(timestamp)
        return f"{staff_id}{ts}"


user_tokenizer = UserTokenGenerator()
