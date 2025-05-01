import qrcode
import argparse
import base64
from PIL import Image
from pyzbar.pyzbar import decode
import io
import os

class QRStego:
    def __init__(self):
        """Initialize the QR code steganography tool."""
        self.lsb_mask = 0xFE  # For masking all but the least significant bit
    
    def create_qr(self, visible_data, error_correction=qrcode.constants.ERROR_CORRECT_H):
        """Create a QR code with the given visible data."""
        qr = qrcode.QRCode(
            version=1,
            error_correction=error_correction,
            box_size=10,
            border=4,
        )
        qr.add_data(visible_data)
        qr.make(fit=True)
        
        # Create an image from the QR Code
        img = qr.make_image(fill_color="black", back_color="white")
        return img
    
    def embed_message_in_payload(self, visible_data, secret_data, password=None):
        """Hide a secret message within QR payload using base64 encoding and a delimiter."""
        # Optionally encrypt the secret message (basic encryption for demo)
        if password:
            # Simple XOR encryption (not secure, just for demonstration)
            secret_bytes = ''.join(chr(ord(a) ^ ord(b % len(password))) 
                           for a, b in zip(secret_data, password * (len(secret_data) // len(password) + 1)))
            secret_data = secret_bytes
        
        # Encode secret data in base64
        encoded_secret = base64.b64encode(secret_data.encode()).decode()
        
        # Combine visible and secret data with a special delimiter
        combined_data = f"{visible_data}###STEGO###${encoded_secret}"
        
        # Create QR code with combined data
        img = self.create_qr(combined_data)
        return img
    
    def embed_message_in_pixels(self, visible_data, secret_data, output_path, password=None):
        """Hide a secret message within the pixel values of a QR code."""
        # Create QR code with visible data
        qr_img = self.create_qr(visible_data)
        
        # Convert to RGB mode if it's not already
        if qr_img.mode != 'RGB':
            qr_img = qr_img.convert('RGB')
        
        # Get image dimensions
        width, height = qr_img.size
        
        # Prepare secret data
        if password:
            # Simple XOR encryption (not secure, just for demonstration)
            secret_bytes = ''.join(chr(ord(a) ^ ord(b % len(password))) 
                           for a, b in zip(secret_data, password * (len(secret_data) // len(password) + 1)))
            secret_data = secret_bytes
        
        # Convert secret message to binary
        binary_secret = ''.join(format(ord(c), '08b') for c in secret_data)
        binary_secret += '00000000'  # End marker
        
        # Check if the image has enough pixels to store the secret
        if len(binary_secret) > (width * height * 3):
            raise ValueError("Secret message is too large for this QR code size")
        
        # Embed length of secret data at the beginning (16 bits = max 65535 chars)
        length_binary = format(len(secret_data), '016b')
        all_binary = length_binary + binary_secret
        
        # Embed data in LSB of pixels
        pixels = qr_img.load()
        idx = 0
        
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                
                # Modify R channel
                if idx < len(all_binary):
                    r = (r & self.lsb_mask) | int(all_binary[idx])
                    idx += 1
                
                # Modify G channel
                if idx < len(all_binary):
                    g = (g & self.lsb_mask) | int(all_binary[idx])
                    idx += 1
                
                # Modify B channel
                if idx < len(all_binary):
                    b = (b & self.lsb_mask) | int(all_binary[idx])
                    idx += 1
                
                pixels[x, y] = (r, g, b)
                
                if idx >= len(all_binary):
                    break
            
            if idx >= len(all_binary):
                break
        
        # Save the image
        qr_img.save(output_path)
        return qr_img
    
    def extract_from_payload(self, image_path, password=None):
        """Extract visible and hidden messages from a QR code payload."""
        # Decode QR code
        qr_data = self.decode_qr(image_path)
        
        if not qr_data:
            return None, None
        
        # Check if the QR contains steganographic data
        if "###STEGO###$" in qr_data:
            visible_data, encoded_secret = qr_data.split("###STEGO###$", 1)
            
            try:
                # Decode from base64
                decoded_secret = base64.b64decode(encoded_secret).decode()
                
                # Decrypt if password was provided
                if password:
                    # Simple XOR decryption
                    secret_data = ''.join(chr(ord(a) ^ ord(b % len(password))) 
                                 for a, b in zip(decoded_secret, password * (len(decoded_secret) // len(password) + 1)))
                    return visible_data, secret_data
                
                return visible_data, decoded_secret
            except Exception as e:
                print(f"Error extracting hidden message: {e}")
                return qr_data, None
        else:
            # No hidden data found in payload
            return qr_data, None
    
    def extract_from_pixels(self, image_path, password=None):
        """Extract hidden message from the pixels of a QR code."""
        try:
            # Load the image
            img = Image.open(image_path)
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            width, height = img.size
            pixels = img.load()
            
            # Extract the binary data
            binary_data = ""
            
            # First extract 16 bits for length
            for y in range(height):
                for x in range(width):
                    if len(binary_data) < 16:
                        r, g, b = pixels[x, y]
                        binary_data += str(r & 1)
                        if len(binary_data) < 16:
                            binary_data += str(g & 1)
                        if len(binary_data) < 16:
                            binary_data += str(b & 1)
            
            # Get the length of the hidden message
            msg_length = int(binary_data[:16], 2)
            binary_data = binary_data[16:]
            bits_needed = msg_length * 8
            
            # Continue extracting remaining bits
            for y in range(height):
                for x in range(width):
                    r, g, b = pixels[x, y]
                    
                    # Skip the pixels we've already processed for length
                    if y == 0 and x < 6:  # Approximately where we left off
                        continue
                    
                    # Extract from R channel
                    binary_data += str(r & 1)
                    
                    # Extract from G channel
                    if len(binary_data) <= bits_needed:
                        binary_data += str(g & 1)
                    
                    # Extract from B channel
                    if len(binary_data) <= bits_needed:
                        binary_data += str(b & 1)
                    
                    if len(binary_data) > bits_needed:
                        break
                
                if len(binary_data) > bits_needed:
                    break
            
            # Convert binary to text
            chunks = [binary_data[i:i+8] for i in range(0, min(len(binary_data), bits_needed), 8)]
            message = ''.join(chr(int(chunk, 2)) for chunk in chunks if len(chunk) == 8)
            
            # Decrypt if password was provided
            if password:
                # Simple XOR decryption
                message = ''.join(chr(ord(a) ^ ord(b % len(password))) 
                          for a, b in zip(message, password * (len(message) // len(password) + 1)))
            
            # Decode visible QR message
            visible_msg = self.decode_qr(image_path)
            
            return visible_msg, message
        
        except Exception as e:
            print(f"Error extracting message from pixels: {e}")
            return self.decode_qr(image_path), None
    
    def decode_qr(self, image_path):
        """Decode a QR code and return its data."""
        try:
            img = Image.open(image_path)
            result = decode(img)
            
            if result:
                return result[0].data.decode('utf-8')
            return None
        except Exception as e:
            print(f"Error decoding QR code: {e}")
            return None


def main():
    parser = argparse.ArgumentParser(description="QR Code Steganography Tool")
    parser.add_argument("--action", required=True, choices=["encode", "decode"],
                        help="Action to perform: encode or decode")
    parser.add_argument("--method", default="payload", choices=["payload", "pixels"],
                        help="Steganography method: payload or pixels (default: payload)")
    parser.add_argument("--visible", help="Visible message for QR code")
    parser.add_argument("--secret", help="Secret message to hide")
    parser.add_argument("--password", help="Optional password for encryption")
    parser.add_argument("--input", help="Input QR code image for decoding")
    parser.add_argument("--output", default="qr_stego_output.png",
                        help="Output filename (default: qr_stego_output.png)")
    
    args = parser.parse_args()
    stego = QRStego()
    
    if args.action == "encode":
        if not args.visible:
            parser.error("--visible message is required for encoding")
        
        if not args.secret:
            parser.error("--secret message is required for encoding")
        
        print(f"Creating QR code with visible message: {args.visible}")
        print(f"Hiding secret message using {args.method} method")
        
        if args.method == "payload":
            img = stego.embed_message_in_payload(args.visible, args.secret, args.password)
            img.save(args.output)
        else:  # pixels method
            stego.embed_message_in_pixels(args.visible, args.secret, args.output, args.password)
        
        print(f"Steganographic QR code saved as {args.output}")
    
    elif args.action == "decode":
        if not args.input or not os.path.exists(args.input):
            parser.error("Valid --input file is required for decoding")
        
        print(f"Analyzing QR code: {args.input}")
        
        # Try both methods if method is not specified
        if args.method == "payload":
            visible, secret = stego.extract_from_payload(args.input, args.password)
        else:  # pixels method
            visible, secret = stego.extract_from_pixels(args.input, args.password)
        
        if visible:
            print(f"Visible message: {visible}")
        else:
            print("No visible message found or could not decode QR code")
        
        if secret:
            print(f"Hidden message: {secret}")
        else:
            # If first method failed, try the other
            if args.method == "payload":
                visible, secret = stego.extract_from_pixels(args.input, args.password)
            else:
                visible, secret = stego.extract_from_payload(args.input, args.password)
            
            if secret:
                print(f"Hidden message (using alternative method): {secret}")
            else:
                print("No hidden message found")


if __name__ == "__main__":
    main()
