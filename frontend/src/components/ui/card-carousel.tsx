"use client"

import React from "react"
import { Swiper, SwiperSlide } from "swiper/react"

import "swiper/css"
import "swiper/css/effect-coverflow"
import "swiper/css/pagination"
import "swiper/css/navigation"
import { SparklesIcon } from "lucide-react"
import {
  Autoplay,
  EffectCoverflow,
  Navigation,
  Pagination,
} from "swiper/modules"

import { Badge } from "./badge"

// Compatible Image component for Vite (replacing next/image)
const Image = ({ src, className, alt, width, height, ...props }: any) => (
  <img src={src} className={className} alt={alt} {...props} />
)

interface CarouselProps {
  images?: { src: string; alt: string }[]
  children?: React.ReactNode[]
  autoplayDelay?: number
  showPagination?: boolean
  showNavigation?: boolean
}

export const CardCarousel: React.FC<CarouselProps> = ({
  images,
  children,
  autoplayDelay = 1500,
  showPagination = true,
  showNavigation = true,
}) => {
  const css = `
  .swiper {
    width: 100%;
    padding-bottom: 50px;
  }
  
  .swiper-slide {
    background-position: center;
    background-size: cover;
    width: 300px;
    /* height: 300px; */
    /* margin: 20px; */
  }
  
  .swiper-slide img {
    display: block;
    width: 100%;
  }
  
  
  .swiper-3d .swiper-slide-shadow-left {
    background-image: none;
  }
  .swiper-3d .swiper-slide-shadow-right{
    background: none;
  }
  `
  return (
    <section className="w-full">
      <style>{css}</style>
      <div className="mx-auto w-full max-w-4xl rounded-[24px] border border-[#25d9f5]/15 p-2 shadow-sm md:rounded-t-[44px]">
        <div className="relative mx-auto flex w-full flex-col rounded-[24px] border border-[#25d9f5]/15 bg-neutral-800/5 p-2 shadow-sm md:items-start md:gap-8 md:rounded-b-[20px] md:rounded-t-[40px] md:p-2">
          <Badge
            variant="outline"
            className="absolute left-4 top-6 rounded-[14px] border border-[#25d9f5]/30 text-base md:left-6 text-[#25d9f5] bg-[#25d9f5]/10"
          >
            <SparklesIcon className="fill-[#25d9f5]/40 stroke-1 text-[#25d9f5] w-4 h-4 mr-1" />{" "}
            Latest component
          </Badge>
          <div className="flex flex-col justify-center pb-2 pl-4 pt-14 md:items-center">
            <div className="flex gap-2">
              <div>
                <h3 className="text-4xl opacity-85 font-bold tracking-tight text-[#d9e3f7]">
                  Card Carousel
                </h3>
                <p className="text-[#bbc9cd]/60">Seamless Images carousel animation.</p>
              </div>
            </div>
          </div>

          <div className="flex w-full items-center justify-center gap-4">
            <div className="w-full">
              <Swiper
                spaceBetween={50}
                autoplay={{
                  delay: autoplayDelay,
                  disableOnInteraction: false,
                }}
                effect={"coverflow"}
                grabCursor={true}
                centeredSlides={true}
                loop={true}
                slidesPerView={"auto"}
                coverflowEffect={{
                  rotate: 0,
                  stretch: 0,
                  depth: 100,
                  modifier: 2.5,
                }}
                pagination={showPagination}
                navigation={
                  showNavigation
                    ? {
                      nextEl: ".swiper-button-next",
                      prevEl: ".swiper-button-prev",
                    }
                    : undefined
                }
                modules={[EffectCoverflow, Autoplay, Pagination, Navigation]}
              >
                {children ? (
                  React.Children.map(children, (child, index) => (
                    <SwiperSlide key={index}>
                      <div className="size-full rounded-3xl">
                        {child}
                      </div>
                    </SwiperSlide>
                  ))
                ) : images ? (
                  <>
                    {images.map((image, index) => (
                      <SwiperSlide key={index}>
                        <div className="size-full rounded-3xl">
                          <Image
                            src={image.src}
                            width={500}
                            height={500}
                            className="size-full rounded-xl"
                            alt={image.alt}
                          />
                        </div>
                      </SwiperSlide>
                    ))}
                    {images.map((image, index) => (
                      <SwiperSlide key={index}>
                        <div className="size-full rounded-3xl">
                          <Image
                            src={image.src}
                            width={200}
                            height={200}
                            className="size-full rounded-xl"
                            alt={image.alt}
                          />
                        </div>
                      </SwiperSlide>
                    ))}
                  </>
                ) : null}
              </Swiper>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
