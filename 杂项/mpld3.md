# mpld3  

> 追了一下前端代码，希望能解决内存泄漏的问题！  

## 前端代码  
```js
// 预先引入d3.js 和mpld3.js  
// 需要创建一个div 并指明id

// 初始化插件，也可以添加自定义插件，建议可以将官方的插件生成的js 代码直接拷贝
// 因为这个东西不会经常改变
mpld3.register_plugin("htmltooltip", HtmlTooltipPlugin);
HtmlTooltipPlugin.prototype = Object.create(mpld3.Plugin.prototype);
HtmlTooltipPlugin.prototype.constructor = HtmlTooltipPlugin;
HtmlTooltipPlugin.prototype.requiredProps = ["id"];
HtmlTooltipPlugin.prototype.defaultProps = {
    labels: null,
    target: null,
    hoffset: 0,
    voffset: 10,
    targets: null
};
function HtmlTooltipPlugin(fig, props) {
    mpld3.Plugin.call(this, fig, props);
};

HtmlTooltipPlugin.prototype.draw = function () {
    var obj = mpld3.get_element(this.props.id);
    var labels = this.props.labels;
    var targets = this.props.targets;
    var tooltip = d3.select("body").append("div")
        .attr("class", "mpld3-tooltip")
        .style("position", "absolute")
        .style("z-index", "10")
        .style("visibility", "hidden");

    obj.elements()
        .on("mouseover", function (d, i) {
            tooltip.html(labels[i])
                .style("visibility", "visible");
        })
        .on("mousemove", function (d, i) {
            tooltip
                .style("top", d3.event.pageY + this.props.voffset + "px")
                .style("left", d3.event.pageX + this.props.hoffset + "px");
        }.bind(this))
        .on("mousedown.callout", function (d, i) {
            window.open(targets[i], "_blank");
        })
        .on("mouseout", function (d, i) {
            tooltip.style("visibility", "hidden");
        });
};

// 绘图
mpld3.draw_figure("div_id",JSON.stringfy(resp.msg))
mpld3.remove_figure("div_id")  // 移除绘图
```