$(document).ready(function(){

    var institutionId = $(".hm-healthmap-map").attr("id");
    $(".hm-loader-dimmer").show();
    $.post("/obtainMeasures", {
        start: null,
        end: null,
        institution: institutionId,
        capitulo: null,
        agrupacion: null,
        cie10: "all"
    }, function(data){
        var gyeData = data.gyeData;
        initMap(" Casos Absolutos", "Pacientes Totales", gyeData, "absolute");
        $(".hm-loader-dimmer").hide();
    });

    // START DATE PICKER
    var dateFormat = "mm/dd/yy",
      from = $( "#from" )
        .datepicker({
          defaultDate: "+1w",
          changeMonth: true,
          changeYear: true,
          dateFormat: 'mm/dd/yy',
          numberOfMonths: 1
        })
        .on( "change", function() {
          to.datepicker( "option", "minDate", getDate( this ) );
        }),
      to = $( "#to" ).datepicker({
        defaultDate: "+1w",
        changeMonth: true,
        changeYear: true,
        dateFormat: 'mm/dd/yy',
        numberOfMonths: 1
      })
      .on( "change", function() {
        from.datepicker( "option", "maxDate", getDate( this ) );
      });

    function getDate( element ) {
      var date;
      try {
        date = $.datepicker.parseDate( dateFormat, element.value );
      } catch( error ) {
        date = null;
      }

      return date;
    }


    // AUTOCOMPLETE

    $.widget( "custom.combobox", {
      _create: function() {
        this.wrapper = $( "<span>" )
          .addClass( "custom-combobox" )
          .insertAfter( this.element );
        this.element.hide();
        this._createAutocomplete(this.element.attr('id'));
        this._createShowAllButton();
      },

      _createAutocomplete: function(id) {
        var selected = this.element.children( ":selected" ),
          value = selected.val() ? selected.text() : "";
        console.log("valor", value);
        console.log("selected", selected);
        this.input = $( "<input class='hm-healthmap-combo-select'>" )
          .appendTo( this.wrapper )
          .val( value )
          .attr( "title", "" )
          .addClass( "custom-combobox-input ui-widget ui-widget-content ui-state-default ui-corner-left" )
          .autocomplete({
            delay: 0,
            minLength: (id === "combobox-cie10") ? 3 : 1,
            source: $.proxy( this, "_source" )
          })
          .tooltip({
            classes: {
              "ui-tooltip": "ui-state-highlight"
            }
          });

        this._on( this.input, {
          autocompleteselect: function( event, ui ) {
            ui.item.option.selected = true;
            this._trigger( "select", event, {
              item: ui.item.option
            });
          },

          autocompletechange: "_removeIfInvalid"
        });
      },

      _createShowAllButton: function() {
        var input = this.input,
          wasOpen = false;

        $( "<a>" )
          .attr( "tabIndex", -1 )
          .attr( "title", "Show All Items" )
          .tooltip()
          .appendTo( this.wrapper )
          .button({
            icons: {
              primary: "ui-icon-triangle-1-s"
            },
            text: false
          })
          .removeClass( "ui-corner-all" )
          .addClass( "custom-combobox-toggle ui-corner-right" )
          .on( "mousedown", function() {
            wasOpen = input.autocomplete( "widget" ).is( ":visible" );
          })
          .on( "click", function() {
            input.trigger( "focus" );

            // Close if already visible
            if ( wasOpen ) {
              return;
            }

            // Pass empty string as value to search for, displaying all results
            input.autocomplete( "search", "" );
          });
      },

      _source: function( request, response ) {
        var matcher = new RegExp( $.ui.autocomplete.escapeRegex(request.term), "i" );
        response( this.element.children( "option" ).map(function() {
          var text = $( this ).text();
          if ( this.value && ( !request.term || matcher.test(text) ) )
            return {
              label: text,
              value: text,
              option: this
            };
        }) );
      },

      _removeIfInvalid: function( event, ui ) {

        // Selected an item, nothing to do
        if ( ui.item ) {
          return;
        }

        // Search for a match (case-insensitive)
        var value = this.input.val(),
          valueLowerCase = value.toLowerCase(),
          valid = false;
        this.element.children( "option" ).each(function() {
          if ( $( this ).text().toLowerCase() === valueLowerCase ) {
            this.selected = valid = true;
            return false;
          }
        });

        // Found a match, nothing to do
        if ( valid ) {
          return;
        }

        // Remove invalid value
        this.input
          .val( "" )
          .attr( "title", value + " didn't match any item" )
          .tooltip( "open" );
        this.element.val( "" );
        this._delay(function() {
          this.input.tooltip( "close" ).attr( "title", "" );
        }, 2500 );
        this.input.autocomplete( "instance" ).term = "";
      },

      _destroy: function() {
        this.wrapper.remove();
        this.element.show();
      }
    });

    var comboboxEdad = $("#combobox-edad");
    var comboboxCie10 = $("#combobox-cie10");
    var comboboxCapitulo = $("#combobox-capitulo");
    var comboboxAgrupacion = $( "#combobox-agrupacion" );
    var filterActionButton = $("#hm-filter-action");

    comboboxEdad.combobox();
    comboboxCapitulo.combobox();
    comboboxAgrupacion.combobox();
    comboboxCie10.combobox();


    // MAPS GENERATION LOGIC

    filterActionButton.click(function(){
        var selectedCie10 = comboboxCie10.next().children(":first").val();
        var selectedAgrupacion = comboboxAgrupacion.next().children(":first").val();
        var selectedCapitulo = comboboxCapitulo.next().children(":first").val();
        var selectedEdad = comboboxEdad.next().children(":first").val();
        var selectedFrom = $("#from").val();
        var selectedEnd = $("#to").val();
        $(".hm-loader-dimmer").show();

        $.post("/obtainMeasures", {
            start: selectedFrom === "" ? null : selectedFrom,
            end: selectedEnd === "" ? null : selectedEnd,
            institution: institutionId,
            edad: selectedEdad === "" ? null : selectedEdad,
            capitulo: selectedCapitulo === "" ? null : selectedCapitulo,
            agrupacion: selectedAgrupacion === "" ? null : selectedAgrupacion,
            cie10: selectedCie10 === "" ? null : selectedCie10
        }, function(data){
            var gyeData = data.gyeData;
            var mapTitle = data.mapTitle;
            var instantMapType = (selectedCie10 === "" && selectedAgrupacion === "" && selectedCapitulo === "") ? "absolute" : 'normalized';
            map.remove();
            initMap("% casos relativos", mapTitle, gyeData, instantMapType);
            $(".hm-loader-dimmer").hide();
        })
    });

});