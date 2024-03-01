import bcrypt


prefix = "SALT="
output = "'" + prefix + str(bcrypt.gensalt())[2:-1] + "'"
print(output, "(paste this to .env file)")
