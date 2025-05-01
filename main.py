from qr_stego import QRStego

# Create an instance of QRStego
stego = QRStego()

# Try to decode the QR code

# visible_msg, secret_msg = stego.extract_from_payload("qr_stego_output.png")
visible_msg, secret_msg = stego.extract_from_payload("no_seceret.png")
# visible_msg, secret_msg = stego.extract_from_payload("seceret.png")

print("Visible message:", visible_msg)
print("Secret message:", secret_msg)




# from qr_stego import QRStego

# # Create an instance of QRStego
# stego = QRStego()

# # Try to decode the QR code
# visible_msg, secret_msg = stego.extract_from_payload("qr_stego_output.png")

# print("Visible message:", visible_msg)
# print("Secret message:", secret_msg)

# # If payload method doesn't work, try pixels method
# if not secret_msg:
#     visible_msg, secret_msg = stego.extract_from_pixels("qr_stego_output.png")
#     print("\nTrying pixels method:")
#     print("Visible message:", visible_msg)
#     print("Secret message:", secret_msg)


# ------------------------------------------------------

# import os
# from stegano import lsb

# # secret_message = "Hello World"
# # if os.path.exists("CIA.png"):
# #     secret = lsb.hide("CIA.png", secret_message)
# #     secret.save("CIA_encrypted.png")
# # else:
# #     print("The file does not exist.")

# message = lsb.reveal("qr_stego_output.png")
# print(message)
