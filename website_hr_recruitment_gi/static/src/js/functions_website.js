 $(document).ready(function() {

    var navListItems = $('ul.setup-panel li a'),
        allWells = $('.setup-content');

    allWells.hide();

    navListItems.click(function(e)
    {
        e.preventDefault();
        var $target = $($(this).attr('href')),
            $item = $(this).closest('li');
        
        if (!$item.hasClass('disabled')) {
            navListItems.closest('li').removeClass('active');
            $item.addClass('active');
            allWells.hide();
            $target.show();
        }
    });
    
    $('ul.setup-panel li.active a').trigger('click');
    
    $('#activate-step-2').on('click', function(e) {

        var partner_name    = $("#partner_name").val();
        var email_from      = $("#email_from").val();
        var phone           = $("#phone").val();
        var emailReg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;


        if(email_from == ""){
            email_from = null 
            alert("Correo electronico invalido");
        } 
        else if(!emailReg.test(email_from)){
            email_from = null 
            alert("Correo electronico invalido");
        }


        if (partner_name && email_from && phone) {


            $('ul.setup-panel li:eq(1)').removeClass('disabled').addClass("active");
            $('ul.setup-panel li a[href="#step-4"]').trigger('click');

        }else{
            alert("Es necesario llenar todos los campos para pasar a la siguiente etapa.");
        }
        
        


    })    

    // $('#activate-step-3').on('click', function(e) {


    //    if ($('input:checkbox[name=internship]:checked').val() == "on") {
    //     $('ul.setup-panel li:eq(3)').removeClass('disabled');
    //     $('ul.setup-panel li a[href="#step-4"]').trigger('click');
    //     // $(this).remove();
    //     }else{
    //         $('ul.setup-panel li:eq(2)').addClass('disabled');
    //         $('ul.setup-panel li:eq(2)').removeClass('disabled');

    //         $('ul.setup-panel li a[href="#step-3"]').trigger('click');
    //     }       


    // })   

    // $('#activate-step-4').on('click', function(e) {

    //     var job1            = $("#job1").val();
    //     var exp_start1      = $("#exp_start1").val();
    //     var exp_end1        = $("#exp_end1").val();
    //     var job_inst1       = $("#job_inst1").val();
    //     var description     = $("#description").val();

    //     if (job1 && exp_start1 && exp_end1 && job_inst1 && description) {

    //         $('ul.setup-panel li:eq(3)').removeClass('disabled');
    //         $('ul.setup-panel li a[href="#step-4"]').trigger('click');
    //         $(this).remove();

    //     }else{
    //         alert("Es necesario al menos mencionar un trabajo y las fechas para poder continuar. Si no tienes experiencia regresa a la sección anterior y activa la casilla de verificacion “soy recién  egresado”.")
    //     }

    // })   


});