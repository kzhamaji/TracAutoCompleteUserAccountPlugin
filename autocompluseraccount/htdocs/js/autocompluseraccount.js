// vim: ts=8:sts=2:sw=2:et
(function($) {
  $(function() {
  
    function get_url (tail) {
      start = $('link[rel="start"]').attr('href');
      elems = start.split('/');
      elems.pop();
      elems.push(tail);
      return elems.join('/');
    }

    function split (val) {
      return val.split(/[,\s]\s*/);
    }
    function extractLast (term) {
      return split(term).pop();
    }

    function render_item ( event, ui ) {
            $(this).data("autocomplete")._renderItem = function( ul, item ) {
              content = '<a>';
              if ( item.avatar ) {
                content += item.avatar + ' ';
              }
              content += item.value;
              if ( item.name && item.name != item.value ) {
                content += '  <span class="username">' + item.name + '</span>';
              }
              content += '</a>';

              return $("<li>")
                .data("item.autocomplete", item )
                .append(content)
                .appendTo(ul);
            };
    }

    function enable_autocomplete ( json ) {

      $('input.autocompluseraccount')
        .autocomplete({
          autoFocus: true,
          create: render_item,
          source: json,
        })

      $('input.autocompluseraccount-multi')
        .bind("keydown", function( event ) {
          if (event.keyCode === $.ui.keyCode.TAB &&
              $(this).autocomplete("instance").menu.active ) {
            event.preventDefault();
          }
        })
        .autocomplete({
          autoFocus: true,
          create: render_item,
          source: function( req, res ) {
            res($.ui.autocomplete.filter(json, extractLast(req.term)));
          },
          focus: function( event, ui ) {
            return false;
          },
          select: function( event, ui ) {
            var terms = split(this.value);
            var sep = this.value.indexOf(',') < 0 ? ' ' : ', ';
            terms.pop();
            terms.push(ui.item.value);
            this.value = terms.join(sep);
            return false;
          },
        })
        .blur(function(){
          this.value = this.value.replace(/,?\s*$/, '');
        })
    }

    function enable_observe (source, sflds, mflds, target, input_pfx, input) {

      targets = $(target)
      if ( targets[0] ) {
        $.each(sflds, function(i,fld){
          selector = input_pfx + fld + ' ' + input;
          targets.observe('added', selector, function( record ) {
            $(this).addClass('autocompluseraccount');
            enable_autocomplete(source);
          });
        });
        $.each(mflds, function(i,fld){
          selector = input_pfx + fld + ' ' + input;
          targets.observe('added', selector, function( record ) {
            $(this).addClass('autocompluseraccount-multi');
            enable_autocomplete(source);
          });
        });
      }

    }


    $.getJSON(get_url('accounts_completion'), function(json) {
      var source = json.users;
      var sflds = json.single;
      var mflds = json.multi;

      enable_observe(source, sflds, mflds,
        '#query #filters table.trac-clause',
        'tbody tr.', 'td.filter input');

      enable_observe(source, sflds, mflds,
        '#batchmod_fieldset table tbody',
        'tr#batchmod_', 'input');

      enable_autocomplete(source);
    });

  });
})(jQuery);
