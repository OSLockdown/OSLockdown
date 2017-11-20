/*
 * Copyright 2009 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
/**
 * 
 */
package com.trustedcs.sb.util;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.security.DigestInputStream;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

/**
 * @author amcgrath
 * 
 */
public class FingerprintHelper {

	/**
	 * Basic IO example using SHA1
	 */
	public static void main(String args[]) throws Exception {
		File file = new File(args[0]);
		String hash = args[1];
		String fingerprint = byteArrayToHexString(getFingerprintBytes(file,hash));
		System.out.println(fingerprint + "  " + file.getName());
	}
	
	/**
	 * 
	 * @param file
	 * @param hashAlgorithm
	 * @return
	 */
	public static byte[] getFingerprintBytes(File file, String hashAlgorithm) 
		throws IOException, NoSuchAlgorithmException {		
		
		MessageDigest md = MessageDigest.getInstance(hashAlgorithm);
		DigestInputStream digestIn = new DigestInputStream(
				new BufferedInputStream(new FileInputStream(file)), md);
		digestIn.on(true);
		for (;;) {
			int iRead = digestIn.read();
			if (iRead < 0) {
				break;
			}
		}
		digestIn.close();
		return md.digest();		
	}

	/**
	 * 
	 * @param file
	 * @return
	 * @throws IOException
	 */
	public static byte[] getSHA1(File file) throws Exception {
		return getFingerprintBytes(file,"SHA1");
	}
	
	/**
	 * 
	 * @param file
	 * @return
	 * @throws IOException
	 */
	public static String getSHA1String(File file) throws Exception {
		return byteArrayToHexString(getFingerprintBytes(file,"SHA1"));
	}
	
	/**
	 * 
	 * @param file
	 * @return
	 * @throws IOException
	 */
	public static byte[] getMD5(File file) throws Exception {
		return getFingerprintBytes(file,"MD5");
	}
	
	/**
	 * 
	 * @param file
	 * @return
	 * @throws IOException
	 */
	public static String getMD5String(File file) throws Exception {
		return byteArrayToHexString(getFingerprintBytes(file,"MD5"));
	}

	/**
	 * Converts a byte to hex digit and writes to the supplied buffer
	 * 
	 * @param b
	 * @param builder
	 *            , StringBuilder
	 */
	public static final void byte2hex(byte b, StringBuilder builder) {

		char[] hexChars = { '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
				'a', 'b', 'c', 'd', 'e', 'f' };

		int high = ((b & 0xf0) >> 4);
		int low = (b & 0x0f);

		builder.append(hexChars[high]);
		builder.append(hexChars[low]);
	}

	/**
	 * Converts a byte array to a hex string
	 * 
	 * @param bytes
	 * @return
	 */
	public static final String byteArrayToHexString(byte[] bytes) {
		StringBuilder builder = new StringBuilder();
		int len = bytes.length;

		for (int i = 0; i < len; i++) {
			byte2hex(bytes[i], builder);
		}

		return builder.toString();
	}
}
