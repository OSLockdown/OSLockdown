/*
 *Copyright 2009-2015 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */
import org.apache.commons.lang.time.DurationFormatUtils;

class DateFormatTagLib {
	
    static namespace = 'dateFormat'
	
    static final String DATE_FORMAT = "E MMM dd HH:mm:ss z yyyy";
	
    /**
     * Displays the day of the month with string modifier st,nd,rd,th depending
     * on what day of the month it is.
     * @param the day is passed as the only parameter
     */
    def dayOfMonth = { attrs ->
        int lastDigit = attrs.day % 10;
        // 10th -> 19th
        out << attrs.day;
        if ( attrs.day >= 10 && attrs.day <= 19 ) {
            out << "th";
        }
        else {
            switch( lastDigit ) {
                case 1:
                out << "st"
                break;
                case 2:
                out << "nd"
                break;
                case 3:
                if ( attrs.day != 13 ) {
                    out << "rd"
                    break;
                }
                default:
                out << "th"
                break;
            }
        }
    }
	
    /**
     * Formats the date passed as a pretty string following the SimpleDateFormat
     *
     */
    def printDate = { attrs ->
        def date = attrs.date;
        if ( date ) {
            out << date.format(DATE_FORMAT);
        }
    }

    /**
     * Formats time into a human reable manner
     */
    def printTime = { attrs ->
        if ( attrs.millis ) {
            try {
                long elapsedTime = attrs.millis.toDouble();
                out << DurationFormatUtils.formatDurationWords(elapsedTime,true,false);
            }
            catch ( Exception e ) {
                out << "Time Error"
            }
        }
        else {
            out << "Time Missing"
        }
    }
}
