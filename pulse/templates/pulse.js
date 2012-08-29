/* Pulse ... */
function pulse()
{
    var img = document.createElement('img')
    
    img.src="http://system.subdimension.co.uk/pulse/log/?referrer="+encodeURIComponent(document.referrer)
}

pulse()