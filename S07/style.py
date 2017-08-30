from IPython.core.display import HTML
HTML("""
<link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.2.11/semantic.min.css">
<!-- <link href="https://fonts.googleapis.com/css?family=Open+Sans:300,400,700" rel="stylesheet"> -->
<link href="custom.css" rel="stylesheet">

<script>
    var code_show=true; //true -> hide code at first

    function code_toggle() {
        // $('div.prompt').hide(); // always hide prompt

        if (code_show){
            $('div.input').hide();
        } else {
            $('div.input').show();
        }
        code_show = !code_show
    }
    $( document ).ready(code_toggle);
</script>

<a class="ui large orange inverted button" style="float:right;" href="javascript:code_toggle()">Toggle Code</a> 
""")