/*
 * Copyright 2014 Forcepoint LLC, and licensed under the GPLv3 License.
 *
 * See 'GPLv3_LICENSE.txt' at the root of the source tree for the full GPLv3 license, or
 * visit https://www.gnu.org/licenses/gpl.html instead.
 */

function MyPickdeleteOption(object,index) {
    object.options[index] = null;
}

function MyPickaddOption(object,text,value) {
    var optionName = new Option(text, value, false, false)
    object.options[object.length] = optionName;
}

function MyPicksort3(elem) {
  var opts = $(elem).find('option');
  opts.sort(function (a,b) { 
//      alert ("Comparing " +a.text + " to " +b.text); 
      return  (a.text < b.text) ? -1 : 1; });
  $(elem).empty().append( opts);
}                        

function MyPickcopySelected(fromObject,toObject) {
    for (var i=0, l=fromObject.options.length;i < l ; i++) {
        if (fromObject.options[i].selected)
            MyPickaddOption(toObject,fromObject.options[i].text,fromObject.options[i].value);
    }
    for (var i=fromObject.options.length-1;i>-1;i--) {
        if (fromObject.options[i].selected)
            MyPickdeleteOption(fromObject,i);
    }
    MyPicksort3(toObject);
    
}

function MyPickselectAll(object) {
  for (var i=0, len=object.options.length;i < len ;i++) {
    object[i].selected = "1"
  }
}   
