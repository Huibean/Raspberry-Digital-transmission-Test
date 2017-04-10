$(document).ready(function() {
  var records_categories = []
  for (var i=1; i<101; i++) {
    records_categories.push(i.toString())
  }
  console.log("loading...")
  console.log("records_categories: " + records_categories)

  $(".container").each(function() {
    var testId = $(this).data("test-id")
    var testTitle = $(this).data("test-title")
    console.log(testId)
    var get_records_url = "/get_records/" + testId
    $.ajax({
      url: get_records_url,
      type: 'GET',
      dataType: 'json',
      complete: function (jqXHR, textStatus) {
        // callback
        console.log("loading complete")
      },
      success: function (data, textStatus, jqXHR) {
        // success callback
        //
        console.log(data)
        window.data = data
        var containerId = 'container-' + testId
        var titleText = '数传测试 - ' + testId + " (" + testTitle +")"

        var series_data = data

        Highcharts.chart(containerId, {
            chart: {
                type: 'area',
                spacingBottom: 30
            },
            title: {
                text: titleText
            },
            subtitle: {
                text: '',
                floating: true,
                align: 'right',
                verticalAlign: 'bottom',
                y: 15
            },
            legend: {
                layout: 'vertical',
                align: 'left',
                verticalAlign: 'top',
                x: 150,
                y: 100,
                floating: true,
                borderWidth: 1,
                backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'
            },
            xAxis: {
                categories: records_categories
                               },
            yAxis: {
                title: {
                    text: '延时'
                },
                labels: {
                    formatter: function () {
                        return this.value;
                    }
                }
            },
            tooltip: {
                formatter: function () {
                    return '<b>' + this.series.name + '</b><br/>' +
                        this.x + ': ' + this.y;
                }
            },
            plotOptions: {
                area: {
                    fillOpacity: 0.5
                }
            },
            credits: {
                enabled: false
            },
            series: series_data
        });
      },
      error: function (jqXHR, textStatus, errorThrown) {
        console.log("something wrong")
        // error callback
      }
    });
  })
})
